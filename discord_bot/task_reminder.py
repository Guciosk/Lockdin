import discord
from datetime import datetime, timedelta
import asyncio
import os
from typing import Dict, List, Optional
import random
from utils import ny_to_utc, utc_to_ny, format_datetime, is_dst_in_eastern_time

class TaskReminder:
    def __init__(self, bot, image_store, accountability_partner):
        self.bot = bot
        self.image_store = image_store
        self.accountability_partner = accountability_partner
        # Exactly 30-second intervals for 5 minutes (10 intervals)
        self.reminder_intervals = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  # 10 reminders at 30-second intervals (5 minutes total)
        self.active_reminders = {}  # Dictionary to track active reminders by task_id
        self.completed_tasks = set()  # Set to track completed tasks
        
    async def check_upcoming_tasks(self):
        """
        Periodically check for tasks that are due within 5 minutes
        """
        while True:
            try:
                # Get current time in UTC
                now = datetime.utcnow()
                print(f"Checking for upcoming tasks at {now.isoformat()}")
                
                # Time 5 minutes from now
                five_min_future = now + timedelta(minutes=5)
                print(f"Looking for tasks due between {now.isoformat()} and {five_min_future.isoformat()}")
                
                # Query Supabase for tasks due in the next 5 minutes
                result = self.image_store.supabase.table('tasks')\
                    .select('*, users(*)')\
                    .eq('status', 'pending')\
                    .gte('due_time', now.isoformat())\
                    .lte('due_time', five_min_future.isoformat())\
                    .execute()
                
                upcoming_tasks = result.data
                print(f"Found {len(upcoming_tasks)} tasks due in the next 5 minutes")
                
                # If no tasks found, log all pending tasks for debugging
                if len(upcoming_tasks) == 0:
                    print("Checking all pending tasks for debugging:")
                    all_pending = self.image_store.supabase.table('tasks')\
                        .select('id, description, due_time, status')\
                        .eq('status', 'pending')\
                        .execute()
                    
                    if all_pending.data:
                        for task in all_pending.data:
                            try:
                                task_due = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
                                time_diff = task_due - now
                                minutes_diff = time_diff.total_seconds() / 60
                                print(f"  Task {task['id']}: {task['description']}")
                                print(f"    Due time: {task['due_time']}")
                                print(f"    Minutes until due: {minutes_diff:.2f}")
                                print(f"    Would be included in upcoming: {0 <= minutes_diff <= 5}")
                            except Exception as e:
                                print(f"    Error parsing due time: {str(e)}")
                    else:
                        print("  No pending tasks found at all.")
                
                # Process each upcoming task
                for task in upcoming_tasks:
                    task_id = task['id']
                    description = task.get('description', 'Unknown task')
                    
                    # Verify the due time is actually within the next 5 minutes
                    try:
                        due_time_str = task['due_time']
                        due_time = datetime.fromisoformat(due_time_str.replace('Z', '+00:00'))
                        
                        time_diff = due_time - now
                        minutes_diff = time_diff.total_seconds() / 60
                        
                        print(f"Task {task_id}: {description}")
                        print(f"  Due time: {due_time.isoformat()}")
                        print(f"  Minutes until due: {minutes_diff:.2f}")
                        
                        # Skip if the task is due more than 5 minutes from now
                        if minutes_diff > 5:
                            print(f"  Task {task_id} is due more than 5 minutes from now. Skipping.")
                            continue
                        
                        # Skip if the task is already past due
                        if minutes_diff < 0:
                            print(f"  Task {task_id} is already past due. Skipping.")
                            continue
                    except Exception as e:
                        print(f"Error parsing due time for task {task_id}: {str(e)}")
                        continue
                    
                    # Get the user associated with this task
                    user_id = task['user_id']
                    print(f"  User ID: {user_id}")
                    
                    # Get the Discord user ID from the users table
                    user_result = self.image_store.supabase.table('users')\
                        .select('discord_user_id')\
                        .eq('id', user_id)\
                        .execute()
                    
                    if not user_result.data or len(user_result.data) == 0:
                        print(f"  No user found for task {task_id}")
                        continue
                    
                    discord_user_id = user_result.data[0]['discord_user_id']
                    print(f"  Discord user ID: {discord_user_id}")
                    
                    # Skip if no Discord user ID or if reminder is already active
                    if not discord_user_id:
                        print(f"  No Discord user ID for task {task_id}")
                        continue
                        
                    if task_id in self.active_reminders:
                        print(f"  Reminder already active for task {task_id}")
                        continue
                    
                    # Check if there are any image submissions for this task
                    try:
                        has_image = await self.image_store.check_task_has_image(task_id)
                        print(f"  Has image submission: {has_image}")
                        
                        # Skip if the task already has an image submission
                        if has_image:
                            print(f"  Task {task_id} already has an image submission. Skipping.")
                            continue
                    except Exception as e:
                        # If there's an error, log it and continue anyway
                        print(f"  Error checking if task has image: {str(e)}")
                    
                    # Start a reminder sequence for this task
                    print(f"  Starting reminder sequence for task {task_id}")
                    asyncio.create_task(self.start_reminder_sequence(task, discord_user_id))
                
                # Also check for tasks that are past due and haven't been completed
                await self.check_past_due_tasks()
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"Error checking upcoming tasks: {str(e)}")
                await asyncio.sleep(30)  # Wait 30 seconds before trying again
    
    async def check_past_due_tasks(self):
        """
        Check for tasks that are past due and mark them as failed
        """
        try:
            # Get all pending tasks
            result = self.image_store.supabase.table('tasks')\
                .select('*, users!inner(*)')\
                .eq('status', 'pending')\
                .execute()
            
            if not result.data:
                return
            
            now_utc = datetime.utcnow()
            buffer_minutes = 5  # Add a 5-minute buffer to prevent premature failures
            
            for task in result.data:
                task_id = task['id']
                
                # Skip if this task is already being processed
                if task_id in self.active_reminders:
                    continue
                
                try:
                    # Parse the due time
                    due_time_str = task['due_time']
                    due_time = datetime.fromisoformat(due_time_str.replace('Z', '+00:00'))
                    
                    # Convert to New York time for logging
                    due_time_ny = utc_to_ny(due_time)
                    
                    # Calculate time difference in minutes
                    time_diff = due_time - now_utc
                    minutes_diff = int(time_diff.total_seconds() / 60)
                    hours_diff = minutes_diff / 60
                    
                    # Log the due time and time difference for debugging
                    print(f"Task {task_id} due time (UTC): {due_time.isoformat()}")
                    print(f"Task {task_id} due time (NY): {due_time_ny.isoformat()}")
                    print(f"Current time (UTC): {now_utc.isoformat()}")
                    print(f"Time difference: {hours_diff:.2f} hours ({minutes_diff} minutes)")
                    
                    # Add buffer time (5 minutes)
                    buffer_time = due_time + timedelta(minutes=buffer_minutes)
                    
                    # Check if the task is past due (with buffer)
                    if now_utc > buffer_time:
                        print(f"Task {task_id} is past due. Due: {due_time.isoformat()}, Now: {now_utc.isoformat()}")
                        
                        # Check if the task has an image submission
                        has_image = await self.image_store.check_task_has_image(task_id)
                        
                        if not has_image:
                            # Mark the task as failed
                            await self.image_store.update_task_status(task_id, 'failed')
                            
                            # Get the Discord user
                            discord_user_id = task['users']['discord_user_id']
                            user = await self.bot.fetch_user(int(discord_user_id))
                            
                            if user:
                                # Send failure notification
                                ai_message = await self.accountability_partner.generate_failure_message(
                                    task_description=task['description'],
                                    due_date=due_time_str,
                                    due_time_local=format_datetime(due_time_ny, True),
                                    task_id=task_id
                                )
                                
                                await user.send(ai_message)
                                await asyncio.sleep(1)
                                await user.send(f"To reset this task, use: `!reset_task {task_id}`")
                                
                                print(f"Marked task {task_id} as failed and notified user {user.name}")
                            else:
                                print(f"Could not find Discord user with ID: {discord_user_id}")
                        else:
                            print(f"Task {task_id} has an image submission, not marking as failed")
                    else:
                        # Task is not past due yet
                        buffer_diff = buffer_time - now_utc
                        buffer_minutes_left = int(buffer_diff.total_seconds() / 60)
                        
                        # Calculate days, hours, minutes for clearer reporting
                        days_left = buffer_minutes_left // (24 * 60)
                        hours_left = (buffer_minutes_left % (24 * 60)) // 60
                        mins_left = buffer_minutes_left % 60
                        
                        time_left_str = ""
                        if days_left > 0:
                            time_left_str += f"{days_left} days, "
                        if hours_left > 0 or days_left > 0:
                            time_left_str += f"{hours_left} hours, "
                        time_left_str += f"{mins_left} minutes"
                        
                        # Format the due date for display
                        due_date_str = due_time.strftime("%Y-%m-%d")
                        due_time_str = due_time.strftime("%H:%M:%S")
                        ny_due_date_str = due_time_ny.strftime("%Y-%m-%d")
                        ny_due_time_str = due_time_ny.strftime("%H:%M:%S")
                        
                        print(f"Task {task_id} is not past due yet.")
                        print(f"  Due on: {due_date_str} at {due_time_str} UTC ({ny_due_date_str} at {ny_due_time_str} NY time)")
                        print(f"  Time left: {time_left_str} ({buffer_minutes_left} total minutes with buffer)")
                
                except Exception as e:
                    print(f"Error processing task {task_id}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error checking past due tasks: {str(e)}")
    
    async def start_reminder_sequence(self, task, discord_user_id):
        """
        Start a sequence of increasingly urgent reminders for a task
        """
        task_id = task['id']
        description = task['description']
        
        # Parse the due time
        try:
            due_time_str = task['due_time']
            due_time = datetime.fromisoformat(due_time_str.replace('Z', '+00:00'))
            print(f"Starting reminder sequence for task {task_id}: {description}")
            print(f"Due time: {due_time.isoformat()}")
            print(f"Discord user ID: {discord_user_id}")
        except Exception as e:
            print(f"Error parsing due time for task {task_id}: {str(e)}")
            return
        
        # Mark this task as having an active reminder
        self.active_reminders[task_id] = True
        print(f"Marked task {task_id} as having an active reminder")
        
        # Initialize conversation history for this task
        self.accountability_partner.clear_conversation(task_id)
        print(f"Cleared conversation history for task {task_id}")
        
        try:
            # Get the Discord user
            print(f"Fetching Discord user with ID: {discord_user_id}")
            try:
                user = await self.bot.fetch_user(int(discord_user_id))
                if user:
                    print(f"Found Discord user: {user.name} (ID: {user.id})")
                else:
                    print(f"Could not find Discord user with ID: {discord_user_id}")
                    del self.active_reminders[task_id]
                    return
            except Exception as e:
                print(f"Error fetching Discord user: {str(e)}")
                del self.active_reminders[task_id]
                return
            
            # Send initial reminder
            print(f"Sending initial reminder for task {task_id} to user {user.name}")
            try:
                await self.send_reminder(user, task, 0, reminder_count=0)
                print(f"Initial reminder sent successfully for task {task_id}")
            except Exception as e:
                print(f"Error sending initial reminder: {str(e)}")
                del self.active_reminders[task_id]
                return
            
            # Send increasingly urgent reminders at intervals
            for i, interval in enumerate(self.reminder_intervals):
                # Check if task is still pending before sending next reminder
                task_status = await self.check_task_status(task_id)
                print(f"Task {task_id} status: {task_status}")
                if task_status != 'pending':
                    print(f"Task {task_id} is no longer pending. Stopping reminders.")
                    break
                
                # Check if there are any image submissions for this task
                try:
                    has_image = await self.image_store.check_task_has_image(task_id)
                    print(f"Task {task_id} has image: {has_image}")
                    if has_image:
                        print(f"Task {task_id} has an image submission. Stopping reminders.")
                        break
                except Exception as e:
                    print(f"Error checking if task has image: {str(e)}")
                
                # Wait for the specified interval
                print(f"Waiting {interval} minutes before sending next reminder for task {task_id}")
                await asyncio.sleep(interval * 60)  # Convert minutes to seconds
                
                # Check again if task is still pending and has no image
                task_status = await self.check_task_status(task_id)
                print(f"Task {task_id} status after waiting: {task_status}")
                if task_status != 'pending':
                    print(f"Task {task_id} is no longer pending. Stopping reminders.")
                    break
                
                try:
                    has_image = await self.image_store.check_task_has_image(task_id)
                    print(f"Task {task_id} has image after waiting: {has_image}")
                    if has_image:
                        print(f"Task {task_id} has an image submission. Stopping reminders.")
                        break
                except Exception as e:
                    print(f"Error checking if task has image: {str(e)}")
                
                # Send next reminder with increased urgency
                reminder_count = i + 1  # Reminder count starts at 0 for the initial reminder
                print(f"Sending reminder #{reminder_count} for task {task_id} to user {user.name}")
                try:
                    await self.send_reminder(user, task, min(10, i + 1), reminder_count=reminder_count)
                    print(f"Reminder #{reminder_count} sent successfully for task {task_id}")
                except Exception as e:
                    print(f"Error sending reminder #{reminder_count}: {str(e)}")
            
            # Clear the active reminder flag
            if task_id in self.active_reminders:
                del self.active_reminders[task_id]
                print(f"Cleared active reminder flag for task {task_id}")
                
            # Clear conversation history after the sequence is complete
            self.accountability_partner.clear_conversation(task_id)
            print(f"Cleared conversation history for task {task_id} after sequence completion")
            
        except Exception as e:
            print(f"Error in reminder sequence for task {task_id}: {str(e)}")
            if task_id in self.active_reminders:
                del self.active_reminders[task_id]
                print(f"Cleared active reminder flag for task {task_id} due to error")
    
    async def check_task_status(self, task_id):
        """
        Check the current status of a task
        """
        try:
            result = self.image_store.supabase.table('tasks')\
                .select('status')\
                .eq('id', task_id)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                print(f"No task found with ID: {task_id}")
                return None
                
            return result.data[0]['status']
        except Exception as e:
            print(f"Error checking task status: {str(e)}")
            return None
    
    async def send_reminder(self, user, task, urgency_level, reminder_count=0):
        """
        Send a reminder message with appropriate urgency level using AI
        """
        try:
            task_id = task['id']
            description = task['description']
            print(f"Preparing reminder for task {task_id}: {description}")
            
            try:
                due_time = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
                print(f"Parsed due time: {due_time.isoformat()}")
            except Exception as e:
                print(f"Error parsing due time: {str(e)}")
                due_time = datetime.utcnow() + timedelta(minutes=5)  # Fallback
                print(f"Using fallback due time: {due_time.isoformat()}")
            
            # Current time in UTC
            now_utc = datetime.utcnow()
            print(f"Current time (UTC): {now_utc.isoformat()}")
            
            # Calculate time remaining
            time_left = due_time - now_utc
            minutes_left = max(0, int(time_left.total_seconds() / 60))
            seconds_left = max(0, int(time_left.total_seconds()) % 60)
            print(f"Time left: {minutes_left} minutes and {seconds_left} seconds")
            
            # Convert UTC due time to New York time for display
            try:
                due_time_ny = utc_to_ny(due_time)
                print(f"Converted due time to NY: {due_time_ny.isoformat()}")
            except Exception as e:
                print(f"Error converting due time to NY: {str(e)}")
                due_time_ny = due_time  # Fallback
            
            # Format the times for display
            try:
                due_time_ny_str = format_datetime(due_time_ny, True)
                print(f"Formatted NY time: {due_time_ny_str}")
            except Exception as e:
                print(f"Error formatting NY time: {str(e)}")
                due_time_ny_str = due_time_ny.isoformat()  # Fallback
            
            # Format time remaining
            time_remaining = f"{minutes_left} minutes and {seconds_left} seconds"
            print(f"Formatted time remaining: {time_remaining}")
            
            # Generate AI reminder message with increasing urgency
            print(f"Generating AI reminder message with urgency level {urgency_level} and reminder count {reminder_count}")
            try:
                ai_message = await self.accountability_partner.generate_reminder_message(
                    task_description=description,
                    time_remaining=time_remaining,
                    urgency_level=urgency_level,
                    due_time_local=due_time_ny_str,
                    task_id=task_id,
                    reminder_count=reminder_count
                )
                print(f"Generated AI message: {ai_message[:50]}...")  # Log first 50 chars
            except Exception as e:
                print(f"Error generating AI message: {str(e)}")
                ai_message = f"⏰ Reminder: Your task \"{description}\" is due soon! You have {time_remaining} left to complete it."
                print(f"Using fallback message: {ai_message}")
            
            # Send the AI-generated message
            print(f"Sending message to user {user.name} (ID: {user.id})")
            try:
                await user.send(ai_message)
                print(f"Message sent successfully to user {user.name}")
            except Exception as e:
                print(f"Error sending message to user: {str(e)}")
                raise  # Re-raise to handle in the calling function
            
            print(f"Sent level {urgency_level} reminder (count: {reminder_count}) to {user.name} for task {task_id}")
            
        except Exception as e:
            print(f"Error sending reminder: {str(e)}")
            raise  # Re-raise to handle in the calling function
    
    async def send_past_due_reminder(self, user, task):
        """
        Send a reminder for a task that is past due
        """
        try:
            task_id = task['id']
            description = task['description']
            due_time = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
            
            # Convert UTC due time to New York time for display
            due_time_ny = utc_to_ny(due_time)
            
            # Format the times for display
            due_time_ny_str = format_datetime(due_time_ny, True)
            
            # Generate AI past due message
            ai_message = await self.accountability_partner.generate_past_due_message(
                task_description=description,
                due_time_local=due_time_ny_str,
                task_id=task_id
            )
            
            # Send the AI-generated message
            await user.send(ai_message)
            
            # Send additional reminder about submitting proof
            await asyncio.sleep(1)  # Wait a second
            await user.send("Remember, you can still submit proof of completion by sending an image in this DM!")
            
            # Send another reminder about resetting the task
            await asyncio.sleep(1)  # Wait another second
            await user.send(f"If you need more time, you can reset this task using: `!reset_task {task_id}`")
            
            print(f"Sent past due reminder to {user.name} for task {task_id}")
            
        except Exception as e:
            print(f"Error sending past due reminder: {str(e)}") 