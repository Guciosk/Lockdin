import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_storage(bucket_name: str, file_path: str, file_content: bytes, content_type: str = None):
    """
    Upload a file to Supabase Storage.
    
    :param bucket_name: The name of the bucket to upload to
    :param file_path: The path to store the file at in the bucket
    :param file_content: The binary content of the file
    :param content_type: The content type of the file (optional)
    :return: The response from Supabase Storage
    """
    # Create the bucket if it doesn't exist
    try:
        supabase.storage.get_bucket(bucket_name)
    except:
        supabase.storage.create_bucket(bucket_name)
    
    # Upload the file
    options = {"content-type": content_type} if content_type else None
    response = supabase.storage.from_(bucket_name).upload(
        file_path,
        file_content,
        file_options=options
    )
    
    return response

def get_public_url(bucket_name: str, file_path: str):
    """
    Get the public URL for a file in Supabase Storage.
    
    :param bucket_name: The name of the bucket
    :param file_path: The path of the file in the bucket
    :return: The public URL of the file
    """
    return supabase.storage.from_(bucket_name).get_public_url(file_path)

