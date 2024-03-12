from dotenv import load_dotenv
import os
import boto3

load_dotenv()
S3_BUCKET = os.getenv("S3_BUCKET")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def generate_presigned_upload_url(file_name, file_type="audio/mpeg"):
    return s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": file_name, "ContentType": file_type},
        ExpiresIn=3600,
    )


def generate_presigned_fetch_url(file_name):
    return s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": S3_BUCKET, "Key": file_name}, ExpiresIn=3600
    )
