"""Storage client for MinIO integration"""
from minio import Minio
from minio.error import S3Error
import io
import logging
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageClient:
    """MinIO storage client wrapper"""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Ensure bucket exists"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise

    async def upload_file(
        self, file_name: str, file_content: bytes, content_type: str = "text/plain"
    ) -> str:
        """Upload file to MinIO"""
        try:
            file_size = len(file_content)
            self.client.put_object(
                self.bucket_name,
                file_name,
                io.BytesIO(file_content),
                file_size,
                content_type=content_type,
            )
            logger.info(f"Uploaded file: {file_name}")
            return file_name
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    async def download_file(self, file_name: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise

    async def delete_file(self, file_name: str) -> None:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, file_name)
            logger.info(f"Deleted file: {file_name}")
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise

    async def list_files(self, prefix: str = "") -> list:
        """List files in bucket"""
        try:
            files = []
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)
            for obj in objects:
                files.append(obj.object_name)
            return files
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            raise

    async def get_presigned_url(self, file_name: str, expiry_seconds: int = 3600) -> str:
        """Get presigned URL for file"""
        try:
            url = self.client.get_presigned_url(
                "GET",
                self.bucket_name,
                file_name,
                expires=timedelta(seconds=expiry_seconds),
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise


# Singleton instance
_storage_client = None


def get_storage_client() -> StorageClient:
    """Get storage client instance"""
    global _storage_client
    if _storage_client is None:
        _storage_client = StorageClient()
    return _storage_client
