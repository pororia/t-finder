from uuid import uuid4
from app.config import settings
from app.core.firebase import get_firebase_app


class StorageService:
    def __init__(self):
        self.app = get_firebase_app()

    async def upload_toilet_photo(self, toilet_id: str, file_bytes: bytes, content_type: str) -> dict:
        from firebase_admin import storage
        ext = content_type.split("/")[-1]
        if ext not in ("jpeg", "png", "webp"):
            ext = "jpg"
        path = f"toilets/{toilet_id}/{uuid4()}.{ext}"
        bucket = storage.bucket(app=self.app)
        blob = bucket.blob(path)
        blob.upload_from_string(file_bytes, content_type=content_type)
        blob.make_public()
        return {
            "image_url": blob.public_url,
            "storage_path": path,
        }

    async def delete_photo(self, storage_path: str):
        from firebase_admin import storage
        bucket = storage.bucket(app=self.app)
        blob = bucket.blob(storage_path)
        if blob.exists():
            blob.delete()
