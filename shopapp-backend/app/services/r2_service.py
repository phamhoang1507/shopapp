import uuid
import io
from pathlib import Path
import boto3
from botocore.config import Config
from PIL import Image
from app.core.config import settings


class R2Service:
    def __init__(self):
        self._client = None
        self.bucket = settings.r2_bucket_name
        self.public_url = settings.r2_public_url.rstrip("/")

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
        return self._client

    def _optimize_image(self, data: bytes, max_size: tuple = (1200, 1200)) -> bytes:
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.LANCZOS)
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=85, optimize=True)
        return output.getvalue()

    async def upload_image(self, data: bytes, folder: str = "products", original_filename: str = "image.jpg") -> dict:
        key = f"{folder}/{uuid.uuid4().hex}.webp"
        optimized = self._optimize_image(data)
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=optimized,
            ContentType="image/webp",
            CacheControl="public, max-age=31536000",
        )
        return {"key": key, "url": f"{self.public_url}/{key}"}

    async def delete_image(self, key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    async def upload_avatar(self, data: bytes, user_id: int) -> dict:
        key = f"avatars/user_{user_id}_{uuid.uuid4().hex[:8]}.webp"
        optimized = self._optimize_image(data, max_size=(400, 400))
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=optimized,
            ContentType="image/webp",
        )
        return {"key": key, "url": f"{self.public_url}/{key}"}


r2_service = R2Service()
