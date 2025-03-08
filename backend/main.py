from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from supabase_client import supabase

from sms_service import (
    send_whatsapp_message, 
    process_incoming_message, 
    process_incoming_message_with_storage,
    get_media_as_base64, 
    download_media
)
from typing import Dict, List, Optional
import json
import os

app = FastAPI()

# Check if we're running on Railway
IS_RAILWAY = os.environ.get("RAILWAY_ENVIRONMENT") is not None

class User(BaseModel):
    username: str
    phone_number: str
    points: int

class Task(BaseModel):
    user_id: int
    description: str
    due_time: str

class FeedPost(BaseModel):
    user_id: int
    task_id: int
    image_url: str
    status: str
    post_content: str = None

@app.post("/users/")
async def create_user(user: User):
    response = supabase.table("users").insert(user.model_dump()).execute()
    if response.data:
        return {"message": "User registered", "user": response.data}
    raise HTTPException(status_code=400, detail="Error registering user")

@app.post("/tasks/")
async def create_task(task: Task):
    response = supabase.table("tasks").insert(task.model_dump()).execute()
    if response.data:
        return {"message": "Task created", "task": response.data}
    raise HTTPException(status_code=400, detail="Error creating task")

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    response = supabase.table("tasks").select("*").eq("task_id", task_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    task = Task(**response.data)
    return task

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    response = supabase.table("users").select("*").eq("user_id", user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    user = User(**response.data)
    return user

@app.post("/feed/")
async def post_to_feed(feed_post: FeedPost):
    response = supabase.table("feed").insert(feed_post.model_dump()).execute()
    if response.data:
        return {"message": "Feed post created", "feed_post": response.data}
    raise HTTPException(status_code=400, detail="Error creating feed post")

# Feed of a specific user
@app.get("/feed/{user_id}")
async def get_user_feed(user_id: int):
    response = supabase.table("feed").select("*").eq("user_id", user_id).execute()
    return response.data if response.data else {"message": "No posts found"}

# For universal feed
@app.get("/feed/")
async def get_all_feed_posts():
    response = supabase.table("feed").select("*").execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="No feed posts found")
    feed_posts = [FeedPost(**post) for post in response.data]
    return feed_posts

@app.post("/message/")
async def send_text(phone_number: str, message: str):
    send_whatsapp_message(phone_number, message)
    return {"message": "Message sent successfully"}

@app.post("/webhook/twilio")
async def twilio_webhook(request: Request):
    """
    Webhook endpoint for receiving messages from Twilio.
    This handles both SMS and WhatsApp messages, including media (images).
    
    Configure this URL in your Twilio console:
    1. Go to https://www.twilio.com/console/phone-numbers/incoming
    2. Select your phone number
    3. Under "Messaging", set the webhook URL to your endpoint (e.g., https://your-domain.com/webhook/twilio)
    """
    # Get form data from the Twilio webhook request
    form_data = await request.form()
    message_data = dict(form_data)
    
    # Process the incoming message
    # If running on Railway, use Supabase Storage for media
    if IS_RAILWAY:
        processed_message = process_incoming_message_with_storage(message_data, bucket_name="notes")
    else:
        processed_message = process_incoming_message(message_data)
    
    try:
        # Get the phone number of the sender
        from_number = processed_message["from_number"]
        
        # Find the user by phone number
        user_response = supabase.table("users").select("*").eq("phone_number", from_number).execute()
        
        if not user_response.data:
            # User not found, create a default response
            auto_reply = "Thanks for your message! Please register first to use our service."
            send_whatsapp_message(from_number, auto_reply)
            return JSONResponse(content={"success": True, "message": "User not found"})
        
        user = user_response.data[0]
        user_id = user.get("id")
        
        # Store the message in the messages table for record-keeping
        message_record = {
            "from_number": processed_message["from_number"],
            "to_number": processed_message["to_number"],
            "body": processed_message["body"],
            "message_sid": processed_message["message_sid"],
            "num_media": processed_message["num_media"],
            "media_items": json.dumps(processed_message["media_items"])
        }
        
        supabase.table("messages").insert(message_record).execute()
        
        # Check if this is a task completion (has media)
        if processed_message["num_media"] > 0:
            # Get the most recent active task for this user
            task_response = supabase.table("tasks").select("*").eq("user_id", user_id).eq("status", "active").order("created_at", desc=True).limit(1).execute()
            
            if task_response.data:
                task = task_response.data[0]
                task_id = task.get("id")
                
                # Create a feed post for the completed task
                for media_item in processed_message["media_items"]:
                    image_url = None
                    
                    # If we have storage info, use the public URL
                    if "storage" in media_item:
                        image_url = media_item["storage"]["public_url"]
                    else:
                        # Otherwise use the Twilio media URL
                        image_url = media_item["url"]
                    
                    # Create a feed post
                    feed_post = {
                        "user_id": user_id,
                        "task_id": task_id,
                        "image_url": image_url,
                        "status": "completed",
                        "post_content": processed_message["body"] if processed_message["body"] else "Task completed"
                    }
                    
                    supabase.table("feed").insert(feed_post).execute()
                
                # Update the task status to completed
                supabase.table("tasks").update({"status": "completed"}).eq("id", task_id).execute()
                
                # Award points to the user
                new_points = user.get("points", 0) + 10  # Award 10 points for completing a task
                supabase.table("users").update({"points": new_points}).eq("id", user_id).execute()
                
                auto_reply = f"Great job completing your task! You've earned 10 points. Your new total is {new_points} points."
            else:
                # No active task found
                auto_reply = "Thanks for sending an image! However, you don't have any active tasks to complete."
        else:
            # This is just a text message
            auto_reply = f"Thanks for your message: '{processed_message['body']}'. To complete a task, please send an image."
        
        # Send the auto-reply
        send_whatsapp_message(from_number, auto_reply)
        
        return JSONResponse(content={"success": True, "message": "Webhook processed successfully"})
    
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

@app.get("/messages/")
async def get_messages(limit: int = 10, offset: int = 0, from_number: Optional[str] = None):
    """
    Retrieve messages from the database.
    
    :param limit: Maximum number of messages to return
    :param offset: Number of messages to skip
    :param from_number: Filter messages by sender's phone number
    :return: List of messages
    """
    try:
        query = supabase.table("messages").select("*").order("created_at", desc=True).limit(limit).offset(offset)
        
        # Apply filter if from_number is provided
        if from_number:
            query = query.eq("from_number", from_number)
        
        response = query.execute()
        
        if not response.data:
            return {"messages": []}
        
        # Parse the media_items JSON string back to a list
        for message in response.data:
            if isinstance(message.get("media_items"), str):
                message["media_items"] = json.loads(message["media_items"])
        
        return {"messages": response.data}
    
    except Exception as e:
        print(f"Error retrieving messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@app.get("/messages/{message_id}")
async def get_message(message_id: int):
    """
    Retrieve a specific message by ID.
    
    :param message_id: The ID of the message to retrieve
    :return: The message details
    """
    try:
        response = supabase.table("messages").select("*").eq("id", message_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Parse the media_items JSON string back to a list
        message = response.data
        if isinstance(message.get("media_items"), str):
            message["media_items"] = json.loads(message["media_items"])
        
        return message
    
    except Exception as e:
        print(f"Error retrieving message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving message: {str(e)}")

@app.get("/messages/{message_id}/media/{media_index}")
async def get_message_media(message_id: int, media_index: int, as_base64: bool = False):
    """
    Retrieve media from a message.
    
    :param message_id: The ID of the message
    :param media_index: The index of the media item to retrieve
    :param as_base64: Whether to return the media as base64 or raw binary
    :return: The media content
    """
    try:
        # Get the message from the database
        response = supabase.table("messages").select("*").eq("id", message_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message = response.data
        
        # Parse the media_items JSON string back to a list
        if isinstance(message.get("media_items"), str):
            media_items = json.loads(message["media_items"])
        else:
            media_items = message.get("media_items", [])
        
        # Check if the media index is valid
        if media_index < 0 or media_index >= len(media_items):
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Get the media URL
        media_url = media_items[media_index]["url"]
        
        if as_base64:
            # Return the media as base64
            media_data = get_media_as_base64(media_url)
            if media_data:
                return media_data
            else:
                raise HTTPException(status_code=500, detail="Failed to download media")
        else:
            # Return the media as raw binary
            content, content_type = download_media(media_url)
            if content and content_type:
                return Response(content=content, media_type=content_type)
            else:
                raise HTTPException(status_code=500, detail="Failed to download media")
    
    except Exception as e:
        print(f"Error retrieving media: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving media: {str(e)}")