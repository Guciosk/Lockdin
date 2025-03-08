import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the bot token and target user ID from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_USER_ID = os.getenv('TARGET_USER_ID')

# Set up intents to receive message content
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance with command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store active DM channels
active_dms = {}

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    
    # Start the task to send messages every 5 seconds
    bot.loop.create_task(send_periodic_messages())

async def send_periodic_messages():
    """Task to send 'Hello World' message every 5 seconds to the target user."""
    await bot.wait_until_ready()  # Wait until the bot is ready
    
    if not TARGET_USER_ID:
        print("Error: No target user ID found. Please set the TARGET_USER_ID environment variable.")
        return
    
    try:
        # Convert the user_id string to an integer
        user_id = int(TARGET_USER_ID)
        
        # Try to fetch the user
        user = await bot.fetch_user(user_id)
        
        if not user:
            print(f"Error: Could not find user with ID: {user_id}")
            return
            
        # Create DM channel
        dm_channel = await user.create_dm()
        active_dms[user_id] = dm_channel
        
        print(f"Starting to send periodic messages to {user.name} (ID: {user_id})")
        
        # Loop to send messages every 5 seconds
        while not bot.is_closed():
            try:
                await dm_channel.send("Hello World")
                print(f"Sent 'Hello World' to {user.name} (ID: {user_id})")
                await asyncio.sleep(5)  # Wait for 5 seconds
            except Exception as e:
                print(f"Error sending message: {str(e)}")
                await asyncio.sleep(5)  # Still wait 5 seconds before retrying
                
    except ValueError:
        print("Error: TARGET_USER_ID must be a valid integer.")
    except discord.errors.NotFound:
        print(f"Error: Could not find user with ID: {TARGET_USER_ID}")
    except Exception as e:
        print(f"Error in periodic message task: {str(e)}")

@bot.command(name='dm')
async def send_dm(ctx, user_id: str, *, message: str):
    """
    Command to send a DM to a user by their ID.
    Usage: !dm <user_id> <message>
    """
    try:
        # Convert the user_id string to an integer
        user_id = int(user_id)
        
        # Try to fetch the user
        user = await bot.fetch_user(user_id)
        
        if user:
            # Send the DM
            dm_channel = await user.create_dm()
            await dm_channel.send(message)
            
            # Store the DM channel for future reference
            active_dms[user_id] = dm_channel
            
            # Confirm the message was sent
            await ctx.send(f"Message sent to {user.name}#{user.discriminator} (ID: {user_id})")
            
            # Fetch and display previous messages from this DM
            async for msg in dm_channel.history(limit=10):
                if msg.author != bot.user:  # Only show messages from the user, not from the bot
                    print(f"Previous message from {user.name}: {msg.content}")
        else:
            await ctx.send(f"Could not find user with ID: {user_id}")
    
    except ValueError:
        await ctx.send("Please provide a valid user ID (numbers only).")
    except discord.errors.NotFound:
        await ctx.send(f"Could not find user with ID: {user_id}")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_message(message):
    """Event triggered when a message is received."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        user_id = message.author.id
        print(f"DM from {message.author.name} (ID: {user_id}): {message.content}")
        
        # Store the DM channel if not already stored
        if user_id not in active_dms:
            active_dms[user_id] = message.channel
            
        # Respond with "good morning"
        try:
            await message.channel.send("good morning")
            print(f"Sent 'good morning' to {message.author.name} (ID: {user_id})")
        except Exception as e:
            print(f"Error sending response: {str(e)}")
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='list_dms')
async def list_active_dms(ctx):
    """Command to list all active DM channels."""
    if not active_dms:
        await ctx.send("No active DM channels.")
        return
    
    dm_list = []
    for user_id, _ in active_dms.items():
        try:
            user = await bot.fetch_user(user_id)
            dm_list.append(f"{user.name}#{user.discriminator} (ID: {user_id})")
        except:
            dm_list.append(f"Unknown User (ID: {user_id})")
    
    await ctx.send("Active DM channels:\n" + "\n".join(dm_list))

@bot.command(name='read_dm')
async def read_dm_history(ctx, user_id: str, limit: int = 10):
    """
    Command to read the DM history with a specific user.
    Usage: !read_dm <user_id> [limit]
    """
    try:
        # Convert the user_id string to an integer
        user_id = int(user_id)
        
        # Check if we have an active DM with this user
        if user_id not in active_dms:
            # Try to create a new DM channel
            try:
                user = await bot.fetch_user(user_id)
                dm_channel = await user.create_dm()
                active_dms[user_id] = dm_channel
            except:
                await ctx.send(f"No active DM channel with user ID: {user_id}")
                return
        
        dm_channel = active_dms[user_id]
        user = await bot.fetch_user(user_id)
        
        # Fetch message history
        messages = []
        async for msg in dm_channel.history(limit=limit):
            author = "Bot" if msg.author == bot.user else f"{user.name}"
            messages.append(f"{author}: {msg.content}")
        
        if messages:
            messages.reverse()  # Show oldest messages first
            await ctx.send(f"DM history with {user.name} (last {len(messages)} messages):\n" + "\n".join(messages))
        else:
            await ctx.send(f"No message history with {user.name}")
    
    except ValueError:
        await ctx.send("Please provide a valid user ID (numbers only).")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
