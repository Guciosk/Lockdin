# Deploying to Railway

This guide explains how to deploy your FastAPI application with Twilio webhook integration to Railway.

## Prerequisites

1. A [Railway](https://railway.app/) account
2. [Railway CLI](https://docs.railway.app/develop/cli) installed (optional, but recommended)
3. Your code pushed to a GitHub repository (for GitHub deployment method)
4. A Supabase project with the required tables and storage bucket

## Supabase Setup

Before deploying to Railway, make sure your Supabase project is set up correctly:

1. Create the required tables using the SQL in `create_messages_table.sql`
2. Create a "notes" bucket in Supabase Storage:
   - Go to your Supabase dashboard
   - Navigate to "Storage"
   - Click "Create a new bucket"
   - Enter "notes" as the bucket name
   - Set the appropriate permissions (public or private)

## Deployment Steps

### Option 1: Deploy from GitHub

1. Log in to your [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" and select "Deploy from GitHub repo"
3. Select your repository and the branch you want to deploy
4. Railway will automatically detect your FastAPI application and build it
5. Once deployed, Railway will provide you with a public URL for your application

### Option 2: Deploy using Railway CLI

1. Install the Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Log in to your Railway account:
   ```bash
   railway login
   ```

3. Initialize a new project (if you haven't already):
   ```bash
   railway init
   ```

4. Link to an existing project (if you already have one):
   ```bash
   railway link
   ```

5. Deploy your application:
   ```bash
   railway up
   ```

## Environment Variables

You need to set the following environment variables in your Railway project:

1. Go to your project in the Railway dashboard
2. Click on the "Variables" tab
3. Add the following variables:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `TWILIO_WHATSAPP_NUMBER`
   - `MY_PHONE_NUMBER`
   - `MY_WHATSAPP_NUMBER`
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your Supabase project API key

## Configuring Twilio Webhook

After deploying to Railway, you'll get a public URL for your application. Use this URL to configure your Twilio webhook:

1. Log in to your [Twilio Console](https://www.twilio.com/console)
2. Navigate to the WhatsApp Sandbox or your WhatsApp number
3. In the "When a message comes in" field, enter your webhook URL:
   - `https://your-railway-app-name.railway.app/webhook/twilio`
4. Make sure the HTTP method is set to `POST`
5. Save your changes

## How the Application Works

When a user sends a message or image to your Twilio WhatsApp number:

1. Twilio forwards the message to your webhook endpoint
2. The webhook processes the message and any attached media
3. If media is attached, it's stored in the "notes" bucket in Supabase Storage
4. The system checks if the user has an active task
5. If there's an active task, it creates a feed post with the image and marks the task as completed
6. The user receives points for completing the task
7. An auto-reply is sent to the user

## Testing Your Deployment

1. Send a message to your Twilio WhatsApp number
2. Check your Railway logs to see if the webhook is being called:
   - Go to your project in the Railway dashboard
   - Click on the "Deployments" tab
   - Select your latest deployment
   - Click on "Logs"
3. You should receive an auto-reply message
4. Check your Supabase database to see if the message was stored
5. If you sent an image, check your Supabase Storage "notes" bucket to see if the image was uploaded

## Monitoring and Scaling

Railway provides built-in monitoring and scaling capabilities:

1. **Monitoring**: Check your application logs and metrics in the Railway dashboard
2. **Scaling**: Railway automatically scales your application based on usage
3. **Custom Domains**: You can add a custom domain to your Railway application in the "Settings" tab

## Troubleshooting

1. **Application not starting**:
   - Check your Railway logs for errors
   - Verify that your Procfile and railway.json are correctly configured
   - Make sure all required environment variables are set

2. **Webhook not receiving messages**:
   - Verify that your Twilio webhook URL is correctly configured
   - Check your Railway logs for incoming requests
   - Make sure your application is running

3. **Database connection issues**:
   - Check your Supabase connection variables
   - Verify that your Supabase database is accessible from Railway

4. **Media not uploading to Supabase**:
   - Verify that your Supabase credentials are correct
   - Check that the "notes" bucket exists in Supabase Storage
   - Ensure the bucket has the appropriate permissions

5. **Auto-replies not sending**:
   - Check your Twilio credentials
   - Verify that the recipient's phone number is in the correct format
   - Check your Railway logs for errors 