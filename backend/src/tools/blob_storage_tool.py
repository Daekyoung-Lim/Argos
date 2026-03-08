import io
from datetime import datetime, timedelta, timezone

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from ..config import get_settings

settings = get_settings()


def upload_bytes_to_blob(file_bytes: bytes, blob_path: str, content_type: str = "image/jpeg") -> str:
    """Upload bytes to Azure Blob Storage and return the blob URL."""
    client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
    blob_client = client.get_blob_client(
        container=settings.azure_storage_container_name,
        blob=blob_path,
    )
    blob_client.upload_blob(io.BytesIO(file_bytes), overwrite=True)
    return blob_client.url


def generate_sas_url(blob_path: str, expiry_minutes: int = 60) -> str:
    """Generate a time-limited SAS URL for a blob."""
    sas_token = generate_blob_sas(
        account_name=settings.azure_storage_account_name,
        container_name=settings.azure_storage_container_name,
        blob_name=blob_path,
        account_key=settings.azure_storage_account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
    )
    return (
        f"https://{settings.azure_storage_account_name}.blob.core.windows.net/"
        f"{settings.azure_storage_container_name}/{blob_path}?{sas_token}"
    )
