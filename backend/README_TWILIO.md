# Twilio Webhook Integration Guide

This guide explains how to set up and use the Twilio webhook to receive messages and images from users.

## Prerequisites

1. A Twilio account with a WhatsApp Sandbox or WhatsApp Business API
2. Your FastAPI backend deployed with a public URL (Railway or other hosting service)
3. The necessary environment variables set up in your `.env` file or hosting platform:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `TWILIO_WHATSAPP_NUMBER`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

## Setting Up the Webhook in Twilio

1. Log in to your [Twilio Console](https://www.twilio.com/console)
2. Navigate to the WhatsApp Sandbox or your WhatsApp number
3. In the "When a message comes in" field, enter your webhook URL:
   - For Railway: `https://your-railway-app-name.railway.app/webhook/twilio`
   - For other hosting: `https://your-domain.com/webhook/twilio`
   - For local development with ngrok: `https://your-ngrok-url.ngrok.io/webhook/twilio`
4. Make sure the HTTP method is set to `POST`
5. Save your changes

## Testing the Webhook

### Local Development
1. Start your FastAPI application:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. If testing locally, start ngrok to expose your local server:
   ```bash
   ngrok http 8000
   ```

### Railway Deployment
1. Deploy your application to Railway (see README_RAILWAY.md for details)
2. Railway will automatically provide you with a public URL

3. Send a message to your Twilio WhatsApp number
4. Check your application logs to see if the webhook is being called
5. You should receive an auto-reply message

## How It Works

When a user sends a message or image to your Twilio WhatsApp number:

1. Twilio forwards the message to your webhook endpoint
2. The webhook processes the message and any attached media
3. If media is attached, it's stored in the "notes" bucket in Supabase Storage
4. The system checks if the user has an active task
5. If there's an active task, it creates a feed post with the image and marks the task as completed
6. The user receives points for completing the task
7. An auto-reply is sent to the user

## Database Schema

The application uses the following database schema:

- **users**: Stores user information and points
  - id (primary key)
  - created_at (timestamp)
  - username (varchar)
  - phone_number (varchar, unique)
  - points (int)

- **tasks**: Stores tasks assigned to users
  - id (primary key)
  - created_at (timestamp)
  - user_id (foreign key to users)
  - description (text)
  - due_time (timestamp)
  - status (varchar)

- **feed**: Stores completed tasks with images
  - id (primary key)
  - created_at (timestamp)
  - user_id (foreign key to users)
  - task_id (foreign key to tasks)
  - image_url (text)
  - status (varchar)
  - post_content (text)

- **messages**: Stores incoming Twilio messages
  - id (primary key)
  - message_sid (text, unique)
  - from_number (text)
  - to_number (text)
  - body (text)
  - num_media (int)
  - media_items (jsonb)
  - created_at (timestamp)
  - processed (boolean)
  - storage_urls (jsonb)

## API Endpoints

### Receiving Messages

The webhook endpoint `/webhook/twilio` automatically processes incoming messages and stores them in the database.

### Retrieving Messages

- Get all messages: `GET /messages/`
  - Query parameters:
    - `limit`: Maximum number of messages to return (default: 10)
    - `offset`: Number of messages to skip (default: 0)
    - `from_number`: Filter messages by sender's phone number (optional)

- Get a specific message: `GET /messages/{message_id}`

### Retrieving Media

- Get media from a message: `GET /messages/{message_id}/media/{media_index}`
  - Query parameters:
    - `as_base64`: Whether to return the media as base64 or raw binary (default: false)

## Supabase Storage

Images sent by users are stored in the "notes" bucket in Supabase Storage. The public URL of the image is stored in the `image_url` field of the feed table.

To create the "notes" bucket in Supabase:

1. Go to your Supabase dashboard
2. Navigate to "Storage"
3. Click "Create a new bucket"
4. Enter "notes" as the bucket name
5. Set the appropriate permissions (public or private)

## Sending Messages

To send a WhatsApp message:

```python
from sms_service import send_whatsapp_message

send_whatsapp_message("+1234567890", "Hello, this is a test message")
```

## Railway-Specific Considerations

When deploying to Railway:

1. **Environment Variables**: Set all required environment variables in the Railway dashboard
2. **File Storage**: Railway instances have ephemeral file systems, so media is automatically stored in Supabase Storage
3. **Logs**: Check Railway logs for debugging webhook issues
4. **Scaling**: Railway automatically scales your application based on usage

For more details on Railway deployment, see the `README_RAILWAY.md` file.

## Troubleshooting

1. **Webhook not receiving messages**:
   - Check that your webhook URL is correctly set in the Twilio console
   - Ensure your server is publicly accessible
   - Check your application logs for errors

2. **Media not uploading to Supabase**:
   - Verify that your Supabase credentials are correct
   - Check that the "notes" bucket exists in Supabase Storage
   - Ensure the bucket has the appropriate permissions

3. **Auto-replies not sending**:
   - Check your Twilio credentials
   - Verify that the recipient's phone number is in the correct format
   - Check your application logs for errors

4. **Tasks not being marked as completed**:
   - Verify that the user has an active task in the database
   - Check that the task status is "active"
   - Ensure the user exists in the database 