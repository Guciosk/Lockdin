import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import supabase
import openai
from ImageStore.image_store import ImageStore
from datetime import datetime
from OpenAI.server_code import analyze_image



# Load environment variables from .env file
load_dotenv()

# Get the bot token
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents to receive message content
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance with command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Create ImageStore instance
image_store = ImageStore()

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    print('Bot is ready to receive and analyze images!')

@bot.event
async def on_message(message):
    """Event triggered when a message is received."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        user_id = str(message.author.id)
        username = message.author.name

        # Handle any attached images
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith('image/'):
                    try:
                        # Download the image
                        image_data = await attachment.read()
                        # Generate a unique filename using timestamp
                        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                        filename = f"{user_id}_{timestamp}_{attachment.filename}"
                        # Store the image
                        image_url = await image_store.store_image(image_data, filename)
                        
                        if image_url:
                            # Store the message with image info in Supabase
                            await image_store.store_message(
                                user_id=user_id,
                                username=username,
                                message_content=message.content or "Image upload",
                                has_image=True,
                                image_url=image_url
                            )
                            
                            # Analyze the image using OpenAI
                            try:
                                # Send a "Processing..." message
                                processing_msg = await message.channel.send("Processing image with AI... Please wait.")
                                
                                # Get custom prompt if provided in the message
                                custom_prompt = message.content if message.content else "Describe this image in detail"
                                
                                # Analyze the image
                                analysis = analyze_image(image_url, custom_prompt)
                                
                                # Send the analysis
                                await message.channel.send(f"**Image Analysis:**\n{analysis}")
                                
                                # Delete the processing message
                                await processing_msg.delete()
                                
                            except Exception as e:
                                print(f"Error analyzing image: {str(e)}")
                                await message.channel.send("Sorry, there was an error analyzing your image.")
                            
                            print(f"Processed image from {username} (ID: {user_id}): {image_url}")
                        else:
                            await message.channel.send("Sorry, there was an error uploading your image.")
                            
                    except Exception as e:
                        print(f"Error processing image: {str(e)}")
                        await message.channel.send("Sorry, there was an error processing your image.")
                    
                    break  # Process only the first image for now
            
        elif message.content:  # Store text messages without images
            # Store the message in Supabase
            await image_store.store_message(
                user_id=user_id,
                username=username,
                message_content=message.content,
                has_image=False
            )

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
