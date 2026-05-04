import boto3
from django.conf import settings
from botocore.config import Config

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)

    def initiate_multipart_upload(self, key, content_type):
        print("start in ing")
        if not self.bucket_name:
            raise ValueError("AWS_STORAGE_BUCKET_NAME is not configured in settings.py")
            
        response = self.s3_client.create_multipart_upload(
            Bucket=self.bucket_name,
            Key=key,
            ContentType=content_type
        )
        print("response",response)
        return response['UploadId']

    def generate_presigned_url(self, key, upload_id, part_number):
        return self.s3_client.generate_presigned_url(
            ClientMethod='upload_part',
            Params={
                'Bucket': self.bucket_name,
                'Key': key,
                'UploadId': upload_id,
                'PartNumber': part_number
            },
            ExpiresIn=3600
        )

    def complete_multipart_upload(self, key, upload_id, parts):
        # parts is a list of {'ETag': '...', 'PartNumber': ...}
        return self.s3_client.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )

    def list_parts(self, key, upload_id):
        try:
            response = self.s3_client.list_parts(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id
            )
            return response.get('Parts', [])
        except Exception:
            return []

    def abort_multipart_upload(self, key, upload_id):
        return self.s3_client.abort_multipart_upload(
            Bucket=self.bucket_name,
            Key=key,
            UploadId=upload_id
        )
