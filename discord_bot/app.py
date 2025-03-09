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
from utils import ny_to_utc, utc_to_ny, format_datetime, is_dst_in_eastern_time



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
task_reminder = TaskReminder(bot, image_store, accountability_partner)

async def initialize_database():
    """
    Initialize the necessary tables in the database if they don't exist
    """
    try:
        # Check if the feed table exists
        try:
            image_store.supabase.table('feed').select('*').limit(1).execute()
            print("Feed table exists")
        except Exception as e:
            print(f"Feed table doesn't exist or error: {str(e)}")
            print("Creating feed table...")
            # We can't create tables through the Supabase JS client, so we'll just log a message
            print("Please create the feed table manually in the Supabase dashboard with the following columns:")
            print("- id (int8, primary key)")
            print("- created_at (timestamp with time zone)")
            print("- user_id (int8)")
            print("- task_id (int8)")
            print("- image_url (text)")
            print("- status (varchar)")
            print("- timestamp (timestamp with time zone)")
            print("- post_content (text)")
        
        # Check if the tasks table exists
        try:
            image_store.supabase.table('tasks').select('*').limit(1).execute()
            print("Tasks table exists")
        except Exception as e:
            print(f"Tasks table doesn't exist or error: {str(e)}")
            print("Creating tasks table...")
            print("Please create the tasks table manually in the Supabase dashboard with the following columns:")
            print("- id (int8, primary key)")
            print("- created_at (timestamp with time zone)")
            print("- user_id (int8)")
            print("- description (text)")
            print("- due_time (timestamp with time zone)")
            print("- status (varchar)")
            print("- confidence_score (float, optional)")
        
        # Check if the users table exists
        try:
            image_store.supabase.table('users').select('*').limit(1).execute()
            print("Users table exists")
        except Exception as e:
            print(f"Users table doesn't exist or error: {str(e)}")
            print("Creating users table...")
            print("Please create the users table manually in the Supabase dashboard with the following columns:")
            print("- id (int8, primary key)")
            print("- created_at (timestamp with time zone)")
            print("- username (varchar)")
            print("- discord_user_id (varchar)")
            print("- points (int8)")
            print("- phone_number (varchar)")
        
        # Check if the notes bucket exists by trying to list files
        try:
            # Try to list files in the bucket instead of getting bucket info
            image_store.supabase.storage.from_('notes').list()
            print("Notes bucket exists and is accessible")
        except Exception as e:
            print(f"Notes bucket doesn't exist or error: {str(e)}")
            print("Please ensure the 'notes' bucket exists in the Supabase storage and is publicly accessible")
    
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    print('Bot is ready to receive and analyze task submissions!')
    
    # Initialize the database
    await initialize_database()
    
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
        
        # If the message starts with a command prefix, don't process it as a regular message
        if message.content.startswith('!'):
            return
            
        if not tasks:
            await message.channel.send("You don't have any active tasks or your Discord account is not linked to a Lockdin account.")
            await message.channel.send("To create a new account, use: `!create_account <username>`")
            await message.channel.send("To link an existing account, use: `!link <username>`")
            return
            
        # Filter for pending tasks only
        pending_tasks = [task for task in tasks if task['status'] == 'pending']
        
        if not pending_tasks:
            await message.channel.send("You don't have any pending tasks. Use `!create_task` to create a new task.")
            return
        
        # Get the first pending task
        task = pending_tasks[0]
        
        # Check if the task already has an image submission
        has_image = await image_store.check_task_has_image(task['id'])
        if has_image:
            await message.channel.send(f"Your task \"{task['description']}\" is already completed. No need for another submission.")
            await message.channel.send("If you want to create a new task, use: `!create_task <description> | YYYY-MM-DD HH:MM`")
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
                            # Check if this is a placeholder URL due to storage error
                            is_placeholder = "placeholder.com" in image_url
                            if is_placeholder:
                                await message.channel.send("⚠️ Warning: There was an issue storing your image in our storage system, but we'll continue processing your submission.")
                            
                            # Get the first pending task
                            task = pending_tasks[0]
                            
                            # Store the message with image info in Supabase
                            await image_store.store_message(
                                user_id=task['user_id'],
                                username=username,
                                message_content=message.content or "Task submission",
                                has_image=True,
                                image_url=image_url,
                                task_id=task['id']
                            )
                            
                            # Analyze the image and generate response
                            try:
                                # Send a "Processing..." message
                                processing_msg = await message.channel.send("Analyzing your task submission... Please wait.")
                                
                                # Analyze the image
                                image_analysis = analyze_image(image_url, "Analyze this task submission and describe what work has been done")
                                
                                # Generate accountability response
                                response_data = await accountability_partner.generate_response(
                                    task_description=task['description'],
                                    due_date=task['due_time'],
                                    submitted_notes=message.content or "",
                                    image_analysis=image_analysis
                                )
                                
                                # Update task status and scores
                                if response_data['meets_criteria']:
                                    await image_store.update_task_status(
                                        task['id'],
                                        'completed',
                                        response_data['confidence']
                                    )
                                    
                                    # Also update the feed entry status
                                    try:
                                        image_store.supabase.table('feed')\
                                            .update({'status': 'completed'})\
                                            .eq('task_id', task['id'])\
                                            .execute()
                                    except Exception as e:
                                        print(f"Error updating feed status: {str(e)}")
                                    
                                    # Award points to the user
                                    user_result = image_store.supabase.table('users')\
                                        .select('points')\
                                        .eq('discord_user_id', discord_user_id)\
                                        .execute()
                                    
                                    if user_result.data and len(user_result.data) > 0:
                                        current_points = user_result.data[0]['points'] or 0
                                        new_points = current_points + 25  # Award 25 points for completion
                                        
                                        # Update user points
                                        image_store.supabase.table('users')\
                                            .update({'points': new_points})\
                                            .eq('discord_user_id', discord_user_id)\
                                            .execute()
                                        
                                        # Add points info to response
                                        response_data['response'] += f"\n\n🎉 **Congratulations!** You earned 25 points for completing this task!\nYour new point total is: {new_points} points"
                                else:
                                    await image_store.update_task_status(
                                        task['id'],
                                        'pending',
                                        response_data['confidence']
                                    )
                                    
                                    # Add encouragement to response
                                    response_data['response'] += "\n\nYour submission doesn't fully meet the criteria for this task. Please try again with a more complete submission to earn points."
                                    
                                    # Also update the feed entry status to indicate it was unsuccessful
                                    try:
                                        image_store.supabase.table('feed')\
                                            .update({'status': 'unsuccessful'})\
                                            .eq('task_id', task['id'])\
                                            .execute()
                                    except Exception as e:
                                        print(f"Error updating feed status: {str(e)}")
                                    
                                    # Add explicit message about trying again
                                    await asyncio.sleep(1)  # Wait a second
                                    await message.channel.send("**You can try again by sending another image that better demonstrates your completed task.**")
                                
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
            if pending_tasks:
                await image_store.store_message(
                    user_id=pending_tasks[0]['user_id'],
                    username=username,
                    message_content=message.content,
                    has_image=False,
                    image_url=None,
                    task_id=pending_tasks[0]['id']
                )
                
                # Remind the user that they need to submit an image
                await message.channel.send("I've recorded your message, but remember that you need to submit an image to complete your task and earn points!")
                await message.channel.send("Please attach an image showing your completed task.")
            else:
                await message.channel.send("You don't have any pending tasks. Use `!create_task` to create a new task.")

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
        
        await ctx.send(f"Testing AI-generated reminder system with task: **{test_task['description']}**")
        await ctx.send("You will receive a series of increasingly urgent AI-generated reminders.")
        await ctx.send("These reminders simulate what you would receive as your task deadline approaches.")
        await ctx.send("Each reminder will become more aggressive as the urgency increases.")
        
        # Send test reminders with increasing urgency
        for i in range(8):
            await ctx.send(f"\n**Testing urgency level {i}:**")
            await task_reminder.send_reminder(ctx.author, test_task, i)
            await asyncio.sleep(3)  # Longer delay between test messages for readability
        
        # Also test the past due reminder
        await ctx.send("\n**Testing past due reminder:**")
        await task_reminder.send_past_due_reminder(ctx.author, test_task)
        
        # Also test the failure message
        await ctx.send("\n**Testing failure message:**")
        failure_message = await accountability_partner.generate_failure_message(
            task_description=test_task['description'],
            due_date=test_task['due_time']
        )
        await ctx.send(failure_message)
        
        await ctx.send("\nReminder test complete! This demonstrates how the AI will remind you about upcoming tasks with increasing urgency.")
        
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
• `!tasks [status]` - View your tasks (optional: specify 'pending', 'completed', or 'failed')
• `!reset_task <task_id>` - Reset a task's status to pending if it was incorrectly marked as failed
• `!testreminder [task_id]` - Test the AI reminder system with a specific task or your first pending task

**System Commands:**
• `!help` - Show this help message
• `!storage_status` - Check the status of the storage system (for troubleshooting)

**How to use:**
1. First, create an account with `!create_account <username>` or link your existing account with `!link <username>`
2. Create tasks using `!create_task` or in the Lockdin app
3. The AI will remind you when tasks are due within 5 minutes
4. Submit task completions by sending an image in this DM

**Task Submission & Points:**
• You MUST submit an image showing your completed task to earn points
• Text-only submissions will not earn points
• You'll earn 25 points for each completed task
• If you don't submit an image by the due date, the task will be marked as failed
• If a task is incorrectly marked as failed, use `!reset_task <task_id>` to reset it

**AI Reminder System:**
• The AI sends dynamic, personalized reminders every 30 seconds when a task is due within 5 minutes
• Reminders become increasingly urgent and aggressive as the deadline approaches
• The AI adapts its tone and language based on the urgency level
• Multiple reminder messages will be sent for urgent deadlines
• Past due tasks will receive final AI-generated reminders to submit proof immediately

**Examples:**
• `!create_account john_doe`
• `!create_task Complete math homework | 2023-12-31 23:59`
• `!tasks pending`
• `!reset_task 123`

**Time Zones:**
• All times are entered in New York time (Eastern Time)
• The system automatically converts to UTC for storage
• Due dates are displayed in both New York time and UTC

For more help, visit the Lockdin website or contact support.
"""
    await ctx.send(help_text)

# Add a command to view pending tasks
@bot.command(name='tasks')
async def view_tasks(ctx, status: str = None):
    """View your tasks (optional: specify 'pending', 'completed', or 'failed')"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return
    
    discord_user_id = str(ctx.author.id)
    
    try:
        # Get tasks for the user
        tasks = await image_store.get_user_tasks(discord_user_id)
        
        if not tasks:
            await ctx.send("You don't have any tasks or your Discord account is not linked to a Lockdin account.")
            await ctx.send("To create a new account, use: `!create_account <username>`")
            await ctx.send("To link an existing account, use: `!link <username>`")
            return
        
        # Filter by status if specified
        if status:
            status = status.lower()
            if status in ['pending', 'completed', 'failed']:
                tasks = [task for task in tasks if task['status'].lower() == status]
            else:
                await ctx.send(f"Invalid status: {status}. Please use 'pending', 'completed', or 'failed'.")
                return
        
        # Separate tasks by status
        pending_tasks = [task for task in tasks if task['status'].lower() == 'pending']
        completed_tasks = [task for task in tasks if task['status'].lower() == 'completed']
        failed_tasks = [task for task in tasks if task['status'].lower() == 'failed']
        
        # Convert UTC times to New York time for display
        for task_list in [pending_tasks, completed_tasks, failed_tasks]:
            for task in task_list:
                try:
                    due_time = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
                    
                    # Convert to New York time using our utility function
                    due_time_ny = utc_to_ny(due_time)
                    
                    # Add formatted time strings to the task
                    task['due_time_ny'] = format_datetime(due_time_ny, True)
                    task['due_time_utc'] = format_datetime(due_time, True)
                except Exception as e:
                    task['due_time_ny'] = "Unknown"
                    task['due_time_utc'] = "Unknown"
                    print(f"Error converting time for task {task['id']}: {str(e)}")
        
        # Display tasks based on what was requested or show all by default
        if status == 'pending' or not status:
            if pending_tasks:
                await ctx.send(f"**Your Pending Tasks ({len(pending_tasks)}):**")
                for i, task in enumerate(pending_tasks, 1):
                    await ctx.send(f"{i}. **{task['description']}**\n   Due: {task['due_time_ny']} (New York time)\n   ID: {task['id']}\n   Status: {task['status']}")
            elif not status:  # Only show this message if no status was specified
                await ctx.send("You don't have any pending tasks.")
        
        if status == 'completed' or not status:
            if completed_tasks:
                await ctx.send(f"**Your Completed Tasks ({len(completed_tasks)}):**")
                for i, task in enumerate(completed_tasks, 1):
                    await ctx.send(f"{i}. **{task['description']}**\n   Due: {task['due_time_ny']} (New York time)\n   ID: {task['id']}\n   Status: {task['status']}")
            elif not status:  # Only show this message if no status was specified
                await ctx.send("You don't have any completed tasks.")
        
        if status == 'failed' or not status:
            if failed_tasks:
                await ctx.send(f"**Your Failed Tasks ({len(failed_tasks)}):**")
                for i, task in enumerate(failed_tasks, 1):
                    await ctx.send(f"{i}. **{task['description']}**\n   Due: {task['due_time_ny']} (New York time)\n   ID: {task['id']}\n   Status: {task['status']}")
            elif not status:  # Only show this message if no status was specified
                await ctx.send("You don't have any failed tasks.")
        
        # If no tasks were found for the specified status
        if status and not (pending_tasks or completed_tasks or failed_tasks):
            await ctx.send(f"You don't have any {status} tasks.")
        
        # Add a note about resetting failed tasks
        if failed_tasks and (status == 'failed' or not status):
            await ctx.send("\nTo reset a failed task to pending, use: `!reset_task <task_id>`")
    
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
        # Parse the due date (in New York time)
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
        
        # Convert New York time to UTC using our utility function
        due_date_utc = ny_to_utc(due_date)
        
        # Check if the due date is in DST for logging
        is_dst = is_dst_in_eastern_time(due_date)
        print(f"Due date: {due_date}, Is DST: {is_dst}, UTC: {due_date_utc}")
        
        # Format for display
        ny_time_str = format_datetime(due_date, True)
        utc_time_str = format_datetime(due_date_utc, True)
        
        # Create the task with UTC time
        task_data = {
            'user_id': user_id,
            'description': description,
            'due_time': due_date_utc.isoformat(),
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
            await ctx.send(f"Due date: {ny_time_str} (New York time) or {utc_time_str} (UTC)")
            await ctx.send("You'll receive reminders as the due date approaches.")
        else:
            await ctx.send("Failed to create task. Please try again.")
    
    except ValueError:
        await ctx.send("Invalid date format. Please use: YYYY-MM-DD HH:MM")
        await ctx.send("Example: 2023-12-31 23:59")
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        await ctx.send(f"An error occurred while creating your task: {str(e)}")

# Add a command to check the storage status
@bot.command(name='storage_status')
async def storage_status(ctx):
    """Check the status of the storage system"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs for security reasons.")
        return
    
    try:
        # Check if the notes bucket exists
        try:
            files = image_store.supabase.storage.from_('notes').list()
            await ctx.send(f"✅ Notes bucket exists and is accessible.")
            await ctx.send(f"Found {len(files)} files in the bucket.")
            
            # List a few files as examples
            if files:
                file_list = "\n".join([f"- {file.get('name')}" for file in files[:5]])
                await ctx.send(f"Sample files:\n{file_list}")
                if len(files) > 5:
                    await ctx.send(f"...and {len(files) - 5} more files.")
        except Exception as e:
            await ctx.send(f"❌ Error accessing notes bucket: {str(e)}")
            
            # Try to create the bucket
            try:
                image_store.supabase.storage.create_bucket('notes', {'public': True})
                await ctx.send("✅ Created notes bucket successfully.")
            except Exception as create_error:
                await ctx.send(f"❌ Could not create notes bucket: {str(create_error)}")
                await ctx.send("Please create the notes bucket manually in the Supabase dashboard.")
        
        # Check if the feed table exists
        try:
            result = image_store.supabase.table('feed').select('*').limit(5).execute()
            await ctx.send(f"✅ Feed table exists and has {len(result.data)} entries (showing up to 5).")
        except Exception as e:
            await ctx.send(f"❌ Error accessing feed table: {str(e)}")
        
        # Check if the tasks table exists
        try:
            result = image_store.supabase.table('tasks').select('*').limit(5).execute()
            await ctx.send(f"✅ Tasks table exists and has {len(result.data)} entries (showing up to 5).")
        except Exception as e:
            await ctx.send(f"❌ Error accessing tasks table: {str(e)}")
        
        # Check if the users table exists
        try:
            result = image_store.supabase.table('users').select('*').limit(5).execute()
            await ctx.send(f"✅ Users table exists and has {len(result.data)} entries (showing up to 5).")
        except Exception as e:
            await ctx.send(f"❌ Error accessing users table: {str(e)}")
    
    except Exception as e:
        await ctx.send(f"❌ Error checking storage status: {str(e)}")

# Add a command to reset a task's status
@bot.command(name='reset_task')
async def reset_task(ctx, task_id: str = None):
    """Reset a task's status to pending"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs for security reasons.")
        return
    
    if not task_id:
        await ctx.send("Please provide a task ID. Example: `!reset_task 123`")
        return
    
    discord_user_id = str(ctx.author.id)
    
    try:
        # Get the user's tasks
        tasks = await image_store.get_user_tasks(discord_user_id)
        
        # Find the specific task
        task = next((t for t in tasks if str(t['id']) == task_id), None)
        
        if not task:
            await ctx.send(f"No task found with ID {task_id} for your account.")
            return
        
        # Get the current status
        current_status = task['status']
        
        # Reset the task status to pending
        result = image_store.supabase.table('tasks')\
            .update({'status': 'pending'})\
            .eq('id', task_id)\
            .execute()
        
        if result.data:
            await ctx.send(f"✅ Task '{task['description']}' has been reset from '{current_status}' to 'pending'.")
            await ctx.send("You can now submit an image for this task.")
        else:
            await ctx.send("Failed to reset task. Please try again.")
    
    except Exception as e:
        print(f"Error resetting task: {str(e)}")
        await ctx.send(f"An error occurred while resetting the task: {str(e)}")

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
