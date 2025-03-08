import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import supabase
import openai
from ImageStore.image_store import ImageStore
from datetime import datetime
from OpenAI.server_code import analyze_image, OpenAI_Accountability_Partner



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

# Create instances
image_store = ImageStore()
accountability_partner = OpenAI_Accountability_Partner()

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    print('Bot is ready to receive and analyze task submissions!')

@bot.event
async def on_message(message):
    """Event triggered when a message is received."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        discord_user_id= str(message.author.id)
        

        # Get active tasks for the user
        tasks = await image_store.get_user_tasks(discord_user_id)
        active_task = next((task for task in tasks if task['status'] == 'pending'), None)

        # Get active tasks for the user using their discord_user_idfrom users table
        tasks = await image_store.get_user_tasks(discord_user_id)
        if not tasks:
            await message.channel.send("You don't have any active tasks. Please create a task first.")
            return

        # Handle any attached images
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith('image/'):
                    try:
                        # Download the image
                        image_data = await attachment.read()
                        # Generate a unique filename using timestamp
                        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                        filename = f"{discord_user_id}_{timestamp}_{attachment.filename}"
                        # Store the image
                        image_url = await image_store.store_image(image_data, filename)
                        
                        if image_url:
                            # Store the message with image info in Supabase
                            await image_store.store_message(
                                user_id=str(discord_user_id),
                                message_content=message.content or "Task submission",
                                has_image=True,
                                image_url=image_url,
                                task_id=tasks[0]['id']  # Use the first pending task
                            )
                            
                            # Analyze the image and generate response
                            try:
                                # Send a "Processing..." message
                                processing_msg = await message.channel.send("Analyzing your task submission... Please wait.")
                                
                                # Analyze the image
                                image_analysis = analyze_image(image_url, "Analyze this task submission and describe what work has been done")
                                
                                # Generate accountability response
                                response_data = await accountability_partner.generate_response(
                                    task_description=tasks[0]['description'],
                                    due_date=tasks[0]['due_time'],
                                    submitted_notes=message.content or "",
                                    image_analysis=image_analysis
                                )
                                
                                # Update task status and scores
                                if response_data['meets_criteria']:
                                    await image_store.update_task_status(
                                        tasks[0]['id'],
                                        'completed',
                                        response_data['confidence'],
                                        response_data['completion']
                                    )
                                else:
                                    await image_store.update_task_status(
                                        tasks[0]['id'],
                                        'pending',
                                        response_data['confidence'],
                                        response_data['completion']
                                    )
                                
                                # Delete processing message
                                await processing_msg.delete()
                                
                                # Send the analysis and response
                                await message.channel.send(response_data['response'])
                                
                            except Exception as e:
                                print(f"Error analyzing submission: {str(e)}")
                                await message.channel.send("Sorry, there was an error analyzing your submission.")
                            
                            
                        else:
                            await message.channel.send("Sorry, there was an error uploading your submission.")
                            
                    except Exception as e:
                        print(f"Error processing submission: {str(e)}")
                        await message.channel.send("Sorry, there was an error processing your submission.")
                    
                    break  # Process only the first image for now
            
        elif message.content:  # Store text messages without images
            # Store the message in Supabase
            await image_store.store_message(
                user_id=str(discord_user_id),
               
                message_content=message.content,
                has_image=False,
                task_id=tasks[0]['id']
            )

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
