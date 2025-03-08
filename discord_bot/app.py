import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import supabase
import openai
from ImageStore.image_store import ImageStore
from datetime import datetime, timedelta
from OpenAI.server_code import analyze_image, OpenAI_Accountability_Partner
from task_reminder import TaskReminder



# Load environment variables from .env file
load_dotenv()

# Get the bot token
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents to receive message content
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance with command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Create instances
image_store = ImageStore()
accountability_partner = OpenAI_Accountability_Partner()
task_reminder = TaskReminder(bot, image_store)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    print('Bot is ready to receive and analyze task submissions!')
    
    # Start the task reminder background task
    bot.loop.create_task(task_reminder.check_upcoming_tasks())
    print('Task reminder service started!')

@bot.event
async def on_message(message):
    """Event triggered when a message is received."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        discord_user_id = str(message.author.id)
        username = message.author.name
        

        # Get active tasks for the user
        tasks = await image_store.get_user_tasks(discord_user_id)
        
        if not tasks:
            await message.channel.send("You don't have any active tasks or your Discord account is not linked to a Lockdin account.")
            await message.channel.send("To create a new account, use: `!create_account <username>`")
            await message.channel.send("To link an existing account, use: `!link <username>`")
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
                                username=username,
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
                username=username,
                message_content=message.content,
                has_image=False,
                task_id=tasks[0]['id']
            )

# Add a command to manually test the reminder system
@bot.command(name='testreminder')
async def test_reminder(ctx, task_id: str = None):
    """Test the reminder system with a specific task or the first pending task"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return
    
    discord_user_id = str(ctx.author.id)
    
    try:
        if task_id:
            # Get the specific task
            result = image_store.supabase.table('tasks')\
                .select('*')\
                .eq('id', task_id)\
                .execute()
            tasks = result.data
        else:
            # Get the first pending task for the user
            tasks = await image_store.get_user_tasks(discord_user_id)
            tasks = [task for task in tasks if task['status'] == 'pending']
        
        if not tasks:
            await ctx.send("No pending tasks found to test reminders with.")
            return
        
        # Use the first task for testing
        task = tasks[0]
        
        # Create a test task with due time 5 minutes from now
        test_task = task.copy()
        test_task['due_time'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        
        await ctx.send(f"Testing reminder system with task: {test_task['description']}")
        
        # Send test reminders with increasing urgency
        for i in range(5):
            await task_reminder.send_reminder(ctx.author, test_task, i)
            await asyncio.sleep(2)  # Short delay between test messages
        
        await ctx.send("Reminder test complete!")
        
    except Exception as e:
        print(f"Error testing reminder: {str(e)}")
        await ctx.send(f"Error testing reminder: {str(e)}")

# Add a command to create a new Lockdin account
@bot.command(name='create_account')
async def create_account(ctx, username: str = None):
    """Create a new Lockdin account and link it to your Discord account"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs for security reasons.")
        return
    
    if not username:
        await ctx.send("Please provide a username for your new account. Example: `!create_account your_username`")
        return
    
    discord_user_id = str(ctx.author.id)
    discord_username = ctx.author.name
    
    try:
        # Check if the username is already taken
        user_result = image_store.supabase.table('users')\
            .select('*')\
            .eq('username', username)\
            .execute()
        
        if user_result.data and len(user_result.data) > 0:
            await ctx.send(f"Username '{username}' is already taken. Please choose a different username.")
            return
        
        # Check if the Discord user already has an account
        discord_result = image_store.supabase.table('users')\
            .select('*')\
            .eq('discord_user_id', discord_user_id)\
            .execute()
        
        if discord_result.data and len(discord_result.data) > 0:
            await ctx.send(f"You already have a Lockdin account with username '{discord_result.data[0]['username']}'. Use `!link {discord_result.data[0]['username']}` to link it.")
            return
        
        # Create a new user
        new_user = {
            'username': username,
            'discord_user_id': discord_user_id,
            'created_at': datetime.utcnow().isoformat(),
            'points': 0,
            'phone_number': None
        }
        
        result = image_store.supabase.table('users')\
            .insert(new_user)\
            .execute()
        
        if result.data and len(result.data) > 0:
            await ctx.send(f"Successfully created a new Lockdin account with username '{username}' and linked it to your Discord account!")
            await ctx.send("You can now create tasks in the Lockdin app or use the bot to manage your tasks.")
            await ctx.send("Type `!help` to see available commands.")
        else:
            await ctx.send("Failed to create a new account. Please try again later.")
    
    except Exception as e:
        print(f"Error creating account: {str(e)}")
        await ctx.send(f"An error occurred while creating your account: {str(e)}")

# Add a command to link a Discord user to a Lockdin user
@bot.command(name='link')
async def link_user(ctx, username: str = None):
    """Link your Discord account to your Lockdin account"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs for security reasons.")
        return
    
    if not username:
        await ctx.send("Please provide your Lockdin username. Example: `!link admin`")
        return
    
    discord_user_id = str(ctx.author.id)
    
    try:
        # Check if the Lockdin user exists
        user_result = image_store.supabase.table('users')\
            .select('*')\
            .eq('username', username)\
            .execute()
        
        if not user_result.data or len(user_result.data) == 0:
            await ctx.send(f"No Lockdin user found with username: {username}")
            return
        
        user_id = user_result.data[0]['id']
        
        # Update the user's discord_user_id
        update_result = image_store.supabase.table('users')\
            .update({'discord_user_id': discord_user_id})\
            .eq('id', user_id)\
            .execute()
        
        if update_result.data:
            await ctx.send(f"Successfully linked your Discord account to Lockdin user: {username}")
            
            # Get pending tasks for the user
            tasks = await image_store.find_task_by_user_id(discord_user_id)
            pending_tasks = [task for task in tasks if task['status'] == 'pending']
            
            if pending_tasks:
                task_list = "\n".join([f"- {task['description']} (Due: {task['due_time']})" for task in pending_tasks[:5]])
                await ctx.send(f"You have {len(pending_tasks)} pending tasks:\n{task_list}")
                
                if len(pending_tasks) > 5:
                    await ctx.send(f"...and {len(pending_tasks) - 5} more.")
            else:
                await ctx.send("You don't have any pending tasks.")
        else:
            await ctx.send(f"Failed to link your Discord account to Lockdin user: {username}")
    
    except Exception as e:
        print(f"Error linking user: {str(e)}")
        await ctx.send(f"An error occurred while linking your account: {str(e)}")

# Add a help command
@bot.command(name='help')
async def help_command(ctx):
    """Show available commands and how to use the bot"""
    help_text = """
**Lockdin Discord Bot - Help**

This bot helps you stay accountable for your tasks in Lockdin. Here are the available commands:

**Account Commands:**
• `!create_account <username>` - Create a new Lockdin account and link it to your Discord account
• `!link <username>` - Link your Discord account to an existing Lockdin account

**Task Management:**
• `!create_task <description> | <YYYY-MM-DD HH:MM>` - Create a new task with description and due date
• `!tasks` - View your pending tasks
• `!testreminder [task_id]` - Test the reminder system with a specific task or your first pending task

**Help:**
• `!help` - Show this help message

**How to use:**
1. First, create an account with `!create_account <username>` or link your existing account with `!link <username>`
2. Create tasks using `!create_task` or in the Lockdin app
3. The bot will remind you when tasks are due within 5 minutes
4. Submit task completions by sending a message or image in this DM

**Task Submission:**
• Send a message describing your task completion
• Send an image showing your completed task
• The bot will analyze your submission and update your task status

**Examples:**
• `!create_account john_doe`
• `!create_task Complete math homework | 2023-12-31 23:59`
• `!tasks`

For more help, visit the Lockdin website or contact support.
"""
    await ctx.send(help_text)

# Add a command to view pending tasks
@bot.command(name='tasks')
async def view_tasks(ctx):
    """View your pending tasks"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return
    
    discord_user_id = str(ctx.author.id)
    
    try:
        # Get tasks for the user
        tasks = await image_store.find_task_by_user_id(discord_user_id)
        
        if not tasks:
            await ctx.send("You don't have any tasks or your Discord account is not linked to a Lockdin account.")
            await ctx.send("To create a new account, use: `!create_account <username>`")
            await ctx.send("To link an existing account, use: `!link <username>`")
            return
        
        # Filter by status
        pending_tasks = [task for task in tasks if task['status'] == 'pending']
        completed_tasks = [task for task in tasks if task['status'] == 'completed']
        
        if not pending_tasks and not completed_tasks:
            await ctx.send("You don't have any tasks.")
            return
        
        # Format and send pending tasks
        if pending_tasks:
            pending_list = "\n".join([f"• **{task['description']}**\n  Due: {task['due_time']}\n  ID: {task['id']}" for task in pending_tasks[:5]])
            await ctx.send(f"**Your Pending Tasks ({len(pending_tasks)}):**\n{pending_list}")
            
            if len(pending_tasks) > 5:
                await ctx.send(f"...and {len(pending_tasks) - 5} more pending tasks.")
        else:
            await ctx.send("You don't have any pending tasks.")
        
        # Format and send completed tasks (limited to 3)
        if completed_tasks:
            completed_list = "\n".join([f"• {task['description']} (Completed)" for task in completed_tasks[:3]])
            await ctx.send(f"**Recently Completed Tasks ({len(completed_tasks)}):**\n{completed_list}")
            
            if len(completed_tasks) > 3:
                await ctx.send(f"...and {len(completed_tasks) - 3} more completed tasks.")
    
    except Exception as e:
        print(f"Error viewing tasks: {str(e)}")
        await ctx.send(f"An error occurred while retrieving your tasks: {str(e)}")

# Add a command to create a task
@bot.command(name='create_task')
async def create_task(ctx, *, task_info: str = None):
    """Create a new task (format: description | YYYY-MM-DD HH:MM)"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return
    
    discord_user_id = str(ctx.author.id)
    
    # Check if user exists
    user_result = image_store.supabase.table('users')\
        .select('*')\
        .eq('discord_user_id', discord_user_id)\
        .execute()
    
    if not user_result.data or len(user_result.data) == 0:
        await ctx.send("You don't have a Lockdin account linked to your Discord account.")
        await ctx.send("To create a new account, use: `!create_account <username>`")
        await ctx.send("To link an existing account, use: `!link <username>`")
        return
    
    user_id = user_result.data[0]['id']
    
    if not task_info:
        await ctx.send("Please provide task information in the format: `!create_task description | YYYY-MM-DD HH:MM`")
        await ctx.send("Example: `!create_task Complete math homework | 2023-12-31 23:59`")
        return
    
    # Parse task information
    parts = task_info.split('|')
    if len(parts) != 2:
        await ctx.send("Invalid format. Please use: `!create_task description | YYYY-MM-DD HH:MM`")
        return
    
    description = parts[0].strip()
    due_date_str = parts[1].strip()
    
    try:
        # Parse the due date
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
        due_date_utc = due_date.isoformat()
        
        # Create the task
        task_data = {
            'user_id': user_id,
            'description': description,
            'due_time': due_date_utc,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = image_store.supabase.table('tasks')\
            .insert(task_data)\
            .execute()
        
        if result.data and len(result.data) > 0:
            task_id = result.data[0]['id']
            await ctx.send(f"✅ Task created successfully! Task ID: {task_id}")
            await ctx.send(f"Description: {description}")
            await ctx.send(f"Due date: {due_date_str}")
            await ctx.send("You'll receive reminders as the due date approaches.")
        else:
            await ctx.send("Failed to create task. Please try again.")
    
    except ValueError:
        await ctx.send("Invalid date format. Please use: YYYY-MM-DD HH:MM")
        await ctx.send("Example: 2023-12-31 23:59")
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        await ctx.send(f"An error occurred while creating your task: {str(e)}")

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
