# supabase storage

import os
from supabase import create_client, Client

# Initialize Supabase client
bucket_name = os.getenv("SUPABASE_BUCKET_NAME")


supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
    
)


def upload_image(image_path: str, user_id: str):
    # Upload image to supabase storage
    with open(image_path, "rb") as image_file:
        response = supabase.storage.from_(bucket_name).upload(
            f"{user_id}/{image_path}",
            image_file
        )
        
        if response.status_code == 200:
            return response.data[0].url
        else:
            return None
        
        
def get_image_url(user_id: str, image_path: str):
    # Get image URL from supabase storage
    response = supabase.storage.from_(bucket_name).get_public_url(
        f"{user_id}/{image_path}"
    )
    return response.data[0].public_url
