import pandas as pd
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
import io

load_dotenv()

aws_bucket = os.getenv('AWS_BUCKET_NAME')
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
aws_region = os.getenv('AWS_REGION')


def upload_csv_to_s3(data: list[dict], title: str):
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    try:
        csv_body = pd.DataFrame(data).to_csv(index=False).encode('utf-8-sig')
        s3_client.put_object(
            Bucket=aws_bucket,
            Key=title, #파일명
            Body=csv_body
        )

        return f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{title}"
    except ClientError as e:
        print(f"S3 업로드 중 오류 발생: {e}")
        return False
    
def get_s3_to_dataframe(title: str):
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    try:
        response=s3_client.get_object(
            Bucket=aws_bucket,
            Key=title, #파일명
        )
        return pd.read_csv(io.BytesIO(response['Body'].read()))
    except ClientError as e:
        print(f"S3 업로드 중 오류 발생: {e}")
        return False