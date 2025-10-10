
import boto3
import uuid
from fastapi import UploadFile

from src.core.config import settings

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.s3.aws_access_key_id,
            aws_secret_access_key=settings.s3.aws_secret_access_key,
            region_name=settings.s3.region_name,
            endpoint_url=settings.s3.endpoint_url
        )
        self.bucket_name = settings.s3.bucket_name

    def upload_file(self, file: UploadFile) -> tuple[str, str]:
        s3_key = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        self.s3.upload_fileobj(file.file, self.bucket_name, s3_key)
        if settings.s3.endpoint_url:
            public_url = f"{settings.s3.public_url}/{s3_key}"
        else:
            public_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        return public_url, s3_key

s3_service = S3Service()
