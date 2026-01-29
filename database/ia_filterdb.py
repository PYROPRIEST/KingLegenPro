import re
import base64
from struct import pack
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER, MAX_BTN

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------------------
# DATABASE SETUP
# ----------------------------
client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

# ----------------------------
# MEDIA DOCUMENT
# ----------------------------
@instance.register
class Media(Document):
    file_id = fields.StringField(attribute="_id", required=True)
    file_ref = fields.StringField(allow_none=True)
    file_name = fields.StringField(required=True)
    file_size = fields.IntegerField(required=True)
    file_type = fields.StringField(allow_none=True)
    mime_type = fields.StringField(allow_none=True)
    caption = fields.StringField(allow_none=True)

    class Meta:
        indexes = ("$file_name",)
        collection_name = COLLECTION_NAME

# ----------------------------
# SAVE FILE
# ----------------------------
async def save_file(media):
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
    except ValidationError:
        logger.exception("Error saving file in database")
        return False, 2

    try:
        await file.commit()
    except DuplicateKeyError:
        logger.warning(f"{getattr(media, 'file_name', 'NO_FILE')} already exists")
        return False, 0

    logger.info(f"{getattr(media, 'file_name', 'NO_FILE')} saved successfully")
    return True, 1

# ----------------------------
# SEARCH / GET FILES
# ----------------------------
async def get_search_results(query, file_type=None, max_results=MAX_BTN, offset=0):
    query = query.strip()
    if not query:
        raw_pattern = "."
    elif " " not in query:
        raw_pattern = r"(\b|[\.\+\-_])" + query + r"(\b|[\.\+\-_])"
    else:
        raw_pattern = query.replace(" ", r".*[\s\.\+\-_]")

    regex = re.compile(raw_pattern, flags=re.IGNORECASE)

    filter_ = {"$or": [{"file_name": regex}, {"caption": regex}]} if USE_CAPTION_FILTER else {"file_name": regex}

    if file_type:
        filter_["file_type"] = file_type

    total_results = await Media.count_documents(filter_)
    next_offset = offset + max_results
    if next_offset > total_results:
        next_offset = ""

    cursor = Media.find(filter_).sort("$natural", -1).skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results


async def get_file_details(query):
    cursor = Media.find({"file_id": query})
    result = await cursor.to_list(length=1)
    return result

# ----------------------------
# FILE ID ENCODING
# ----------------------------
def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack("<iiqq", int(decoded.file_type), decoded.dc_id, decoded.media_id, decoded.access_hash)
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
