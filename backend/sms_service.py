from twilio.rest import Client
from dotenv import load_dotenv
import os
import requests
import base64
from io import BytesIO
import uuid
from supabase_client import upload_to_storage, get_public_url

load_dotenv()

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.environ.get("MY_PHONE_NUMBER")
MY_WHATSAPP_NUMBER = os.environ.get("MY_WHATSAPP_NUMBER")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# def send_sms(to_phone_number: int, body: str):
#     """
#     Sends an SMS using Twilio's API.

#     :param to_phone_number: Phone number to send the SMS to
#     :param body: The body content of the SMS
#     :return: The response from Twilio's API (message SID, etc.)
#     """
#     message = client.messages.create(
#         body=body,
#         from_=TWILIO_PHONE_NUMBER,
#         to=to_phone_number
#     )
#     # send the message
#     print(f"message.sid: {message.sid}")
#     return message.sid


def send_whatsapp_message(to_phone_number: int, body: str):
    """
    Sends a WhatsApp message using Twilio's API.

    :param to_phone_number: Phone number to send the WhatsApp message to
    :param body: The body content of the WhatsApp message
    :return: The response from Twilio's API (message SID, etc.)
    """
    message = client.messages.create(
        body=body,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_phone_number
    )
    # send the message
    print(f"message.sid: {message.sid}")
    print(f"message.status: {message.status}")
    print(f"message.error_code: {message.error_code}")
    print(f"message.error_message: {message.error_message}")
    print(f"message.num_media: {message.num_media}")
    print(f"message.num_segments: {message.num_segments}")
    print(f"message.price: {message.price}")
    print(f"message.price_unit: {message.price_unit}")
    print(f"message.uri: {message.uri}")
    
    return message.sid

def process_incoming_message(message_data):
    """
    Process incoming messages from Twilio (SMS or WhatsApp).
    
    :param message_data: The message data from Twilio webhook
    :return: Dictionary with processed message information
    """
    result = {
        "from_number": message_data.get("From"),
        "to_number": message_data.get("To"),
        "body": message_data.get("Body", ""),
        "message_sid": message_data.get("MessageSid"),
        "num_media": int(message_data.get("NumMedia", 0)),
        "media_items": []
    }
    
    # Process any media items (images, etc.)
    num_media = int(message_data.get("NumMedia", 0))
    for i in range(num_media):
        media_url = message_data.get(f"MediaUrl{i}")
        media_content_type = message_data.get(f"MediaContentType{i}")
        
        if media_url:
            result["media_items"].append({
                "url": media_url,
                "content_type": media_content_type
            })
    
    return result

def download_media(media_url):
    """
    Download media from a Twilio media URL.
    
    :param media_url: The URL of the media to download
    :return: Tuple of (content, content_type)
    """
    try:
        # Twilio media URLs require authentication
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        response = requests.get(media_url, auth=auth)
        
        if response.status_code == 200:
            content = response.content
            content_type = response.headers.get('Content-Type')
            return content, content_type
        else:
            print(f"Failed to download media: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Error downloading media: {str(e)}")
        return None, None

def get_media_as_base64(media_url):
    """
    Download media from a Twilio media URL and convert it to base64.
    
    :param media_url: The URL of the media to download
    :return: Dictionary with base64 content and content type
    """
    content, content_type = download_media(media_url)
    
    if content and content_type:
        # Convert binary content to base64
        base64_content = base64.b64encode(content).decode('utf-8')
        
        return {
            "content_type": content_type,
            "base64_content": base64_content
        }
    
    return None

def save_media_to_file(media_url, file_path):
    """
    Download media from a Twilio media URL and save it to a file.
    
    :param media_url: The URL of the media to download
    :param file_path: The path to save the file to
    :return: Boolean indicating success or failure
    """
    content, _ = download_media(media_url)
    
    if content:
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the content to the file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error saving media to file: {str(e)}")
    
    return False

def save_media_to_supabase(media_url, bucket_name="notes"):
    """
    Download media from a Twilio media URL and save it to Supabase Storage.
    
    :param media_url: The URL of the media to download
    :param bucket_name: The name of the Supabase Storage bucket to save to (default: "notes")
    :return: Dictionary with file information or None if failed
    """
    content, content_type = download_media(media_url)
    
    if content and content_type:
        try:
            # Generate a unique filename
            extension = content_type.split('/')[-1]
            if extension == 'jpeg':
                extension = 'jpg'
            
            filename = f"{uuid.uuid4()}.{extension}"
            
            # Upload to Supabase Storage
            upload_to_storage(bucket_name, filename, content, content_type)
            
            # Get the public URL
            public_url = get_public_url(bucket_name, filename)
            
            return {
                "filename": filename,
                "content_type": content_type,
                "public_url": public_url,
                "bucket": bucket_name
            }
        except Exception as e:
            print(f"Error saving media to Supabase: {str(e)}")
    
    return None

def process_incoming_message_with_storage(message_data, store_media=True, bucket_name="notes"):
    """
    Process incoming messages from Twilio (SMS or WhatsApp) and store media in Supabase Storage.
    
    :param message_data: The message data from Twilio webhook
    :param store_media: Whether to store media in Supabase Storage
    :param bucket_name: The name of the Supabase Storage bucket to save to (default: "notes")
    :return: Dictionary with processed message information
    """
    result = {
        "from_number": message_data.get("From"),
        "to_number": message_data.get("To"),
        "body": message_data.get("Body", ""),
        "message_sid": message_data.get("MessageSid"),
        "num_media": int(message_data.get("NumMedia", 0)),
        "media_items": []
    }
    
    # Process any media items (images, etc.)
    num_media = int(message_data.get("NumMedia", 0))
    for i in range(num_media):
        media_url = message_data.get(f"MediaUrl{i}")
        media_content_type = message_data.get(f"MediaContentType{i}")
        
        if media_url:
            media_item = {
                "url": media_url,
                "content_type": media_content_type
            }
            
            # Store media in Supabase Storage if requested
            if store_media:
                storage_info = save_media_to_supabase(media_url, bucket_name)
                if storage_info:
                    media_item["storage"] = storage_info
            
            result["media_items"].append(media_item)
    
    return result

# Example of how to use the process_incoming_message function:
# This would be called by your webhook endpoint in main.py
# webhook_data = {
#     "From": "+1234567890",
#     "To": TWILIO_WHATSAPP_NUMBER,
#     "Body": "Hello, this is a test message",
#     "MessageSid": "SM123456789",
#     "NumMedia": "1",
#     "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/AC123/Messages/MM123/Media/ME123",
#     "MediaContentType0": "image/jpeg"
# }
# processed_message = process_incoming_message(webhook_data)
# print(processed_message)

# # run the function
# send_whatsapp_message(MY_WHATSAPP_NUMBER, "Hello, this is a test message")
# # CHECk if message was sent
