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
        # Change to 30-second intervals (0.5 minutes)
        self.reminder_intervals = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  # 10 reminders at 30-second intervals
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
                
                # Query Supabase for tasks due in the next 5 minutes
                result = self.image_store.supabase.table('tasks')\
                    .select('*, users(*)')\
                    .eq('status', 'pending')\
                    .gte('due_time', now.isoformat())\
                    .lte('due_time', five_min_future.isoformat())\
                    .execute()
                
                upcoming_tasks = result.data
                print(f"Found {len(upcoming_tasks)} tasks due in the next 5 minutes")
                
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
                    
                    # Get the Discord user ID from the users table
                    user_result = self.image_store.supabase.table('users')\
                        .select('discord_user_id')\
                        .eq('id', user_id)\
                        .execute()
                    
                    if not user_result.data or len(user_result.data) == 0:
                        print(f"No user found for task {task_id}")
                        continue
                    
                    discord_user_id = user_result.data[0]['discord_user_id']
                    
                    # Skip if no Discord user ID or if reminder is already active
                    if not discord_user_id:
                        print(f"No Discord user ID for task {task_id}")
                        continue
                        
                    if task_id in self.active_reminders:
                        print(f"Reminder already active for task {task_id}")
                        continue
                    
                    # Check if there are any image submissions for this task
                    try:
                        feed_result = self.image_store.supabase.table('feed')\
                            .select('*')\
                            .eq('task_id', task_id)\
                            .not_.is_('image_url', 'null')\
                            .execute()
                        
                        has_submission = feed_result.data and len(feed_result.data) > 0
                        
                        # Skip if the task already has an image submission
                        if has_submission:
                            print(f"Task {task_id} already has an image submission. Skipping.")
                            continue
                    except Exception as e:
                        # If the feed table doesn't exist or there's another error, continue anyway
                        print(f"Error checking feed table: {str(e)}")
                    
                    # Start a reminder sequence for this task
                    print(f"Starting reminder sequence for task {task_id}")
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
        Check for tasks that are past due and haven't been completed
        """
        try:
            # Get current time in UTC
            now = datetime.utcnow()
            print(f"Current time (UTC): {now.isoformat()}")
            
            # Query Supabase for tasks that are past due
            result = self.image_store.supabase.table('tasks')\
                .select('*, users(*)')\
                .eq('status', 'pending')\
                .lt('due_time', now.isoformat())\
                .execute()
            
            past_due_tasks = result.data
            print(f"Found {len(past_due_tasks)} past due tasks")
            
            for task in past_due_tasks:
                task_id = task['id']
                due_time_str = task['due_time']
                description = task['description']
                
                # Parse the due time
                try:
                    due_time = datetime.fromisoformat(due_time_str.replace('Z', '+00:00'))
                    print(f"Task {task_id} due time (UTC): {due_time.isoformat()}")
                    
                    # Convert to New York time for better logging
                    due_time_ny = utc_to_ny(due_time)
                    print(f"Task {task_id} due time (NY): {format_datetime(due_time_ny, True)}")
                    
                    # Double-check if the task is actually past due
                    # Add a 5-minute buffer to avoid marking tasks as failed too early
                    buffer_time = now - timedelta(minutes=5)
                    if due_time > buffer_time:
                        print(f"Task {task_id} is not actually past due or is within buffer period.")
                        print(f"Due (UTC): {format_datetime(due_time, True)}")
                        print(f"Now (UTC): {format_datetime(now, True)}")
                        print(f"Buffer (UTC): {format_datetime(buffer_time, True)}")
                        continue
                except Exception as e:
                    print(f"Error parsing due time for task {task_id}: {str(e)}")
                    continue
                
                # Skip if we've already processed this task
                if task_id in self.completed_tasks:
                    print(f"Task {task_id} already processed")
                    continue
                
                # Mark as processed to avoid duplicate handling
                self.completed_tasks.add(task_id)
                print(f"Processing past due task {task_id}: {description}")
                
                # Get the user associated with this task
                user_id = task['user_id']
                
                # Get the Discord user ID from the users table
                user_result = self.image_store.supabase.table('users')\
                    .select('discord_user_id, points')\
                    .eq('id', user_id)\
                    .execute()
                
                if not user_result.data or len(user_result.data) == 0:
                    print(f"No user found for task {task_id}")
                    continue
                
                discord_user_id = user_result.data[0]['discord_user_id']
                
                if not discord_user_id:
                    print(f"No Discord user ID for task {task_id}")
                    continue
                
                # Check if there are any image submissions for this task
                has_submission = False
                try:
                    feed_result = self.image_store.supabase.table('feed')\
                        .select('*')\
                        .eq('task_id', task_id)\
                        .not_.is_('image_url', 'null')\
                        .execute()
                    
                    has_submission = feed_result.data and len(feed_result.data) > 0
                    print(f"Task {task_id} has image submission: {has_submission}")
                except Exception as e:
                    # If the feed table doesn't exist or there's another error, assume no submission
                    print(f"Error checking feed table: {str(e)}")
                
                # Update task status
                if has_submission:
                    # Task completed with image submission
                    await self.image_store.update_task_status(task_id, 'completed')
                    print(f"Marked task {task_id} as completed")
                    
                    # Award points to the user
                    current_points = user_result.data[0]['points'] or 0
                    new_points = current_points + 25  # Award 25 points for completion
                    
                    # Update user points
                    self.image_store.supabase.table('users')\
                        .update({'points': new_points})\
                        .eq('id', user_id)\
                        .execute()
                    
                    # Notify user
                    try:
                        user = await self.bot.fetch_user(int(discord_user_id))
                        if user:
                            await user.send(f"🎉 **Task Completed!** You earned 25 points for completing your task: \"{task['description']}\"")
                            await user.send(f"Your new point total is: {new_points} points")
                    except Exception as e:
                        print(f"Error notifying user about completed task: {str(e)}")
                else:
                    # Task failed - no image submission
                    # Only mark as failed if it's significantly past due (more than 5 minutes)
                    time_diff = now - due_time
                    minutes_past_due = time_diff.total_seconds() / 60
                    
                    if minutes_past_due > 5:
                        await self.image_store.update_task_status(task_id, 'failed')
                        print(f"Marked task {task_id} as failed ({minutes_past_due:.2f} minutes past due)")
                        
                        # Notify user with AI-generated message
                        try:
                            user = await self.bot.fetch_user(int(discord_user_id))
                            if user:
                                # Convert UTC due time to New York time for display
                                due_time_ny = utc_to_ny(due_time)
                                
                                # Format the times for display
                                due_time_ny_str = format_datetime(due_time_ny, True)
                                
                                # Generate AI response for failed task
                                ai_response = await self.accountability_partner.generate_failure_message(
                                    task_description=task['description'],
                                    due_date=task['due_time'],
                                    due_time_local=due_time_ny_str
                                )
                                
                                await user.send(ai_response)
                                await user.send("No points were awarded. Remember to submit an image next time to earn points!")
                        except Exception as e:
                            print(f"Error notifying user about failed task: {str(e)}")
                    else:
                        print(f"Task {task_id} is only {minutes_past_due:.2f} minutes past due. Not marking as failed yet.")
        
        except Exception as e:
            print(f"Error checking past due tasks: {str(e)}")
            # Continue execution even if there's an error
    
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
        except Exception as e:
            print(f"Error parsing due time for task {task_id}: {str(e)}")
            return
        
        # Mark this task as having an active reminder
        self.active_reminders[task_id] = True
        
        try:
            # Get the Discord user
            user = await self.bot.fetch_user(int(discord_user_id))
            if not user:
                print(f"Could not find Discord user with ID: {discord_user_id}")
                del self.active_reminders[task_id]
                return
            
            # Send initial reminder
            await self.send_reminder(user, task, 0)
            
            # Send increasingly urgent reminders at intervals
            for i, interval in enumerate(self.reminder_intervals):
                # Check if task is still pending before sending next reminder
                task_status = await self.check_task_status(task_id)
                if task_status != 'pending':
                    print(f"Task {task_id} is no longer pending. Stopping reminders.")
                    break
                
                # Check if there are any image submissions for this task
                try:
                    feed_result = self.image_store.supabase.table('feed')\
                        .select('*')\
                        .eq('task_id', task_id)\
                        .not_.is_('image_url', 'null')\
                        .execute()
                    
                    has_submission = feed_result.data and len(feed_result.data) > 0
                    
                    # Skip if the task already has an image submission
                    if has_submission:
                        print(f"Task {task_id} has an image submission. Stopping reminders.")
                        break
                except Exception as e:
                    # If the feed table doesn't exist or there's another error, continue anyway
                    print(f"Error checking feed table: {str(e)}")
                
                # Wait for the specified interval (convert to seconds)
                await asyncio.sleep(interval * 60)
                
                # Check again if task is still pending
                task_status = await self.check_task_status(task_id)
                if task_status != 'pending':
                    print(f"Task {task_id} is no longer pending. Stopping reminders.")
                    break
                
                # Check again for image submissions
                try:
                    feed_result = self.image_store.supabase.table('feed')\
                        .select('*')\
                        .eq('task_id', task_id)\
                        .not_.is_('image_url', 'null')\
                        .execute()
                    
                    has_submission = feed_result.data and len(feed_result.data) > 0
                    
                    # Skip if the task already has an image submission
                    if has_submission:
                        print(f"Task {task_id} has an image submission. Stopping reminders.")
                        break
                except Exception as e:
                    # If the feed table doesn't exist or there's another error, continue anyway
                    print(f"Error checking feed table: {str(e)}")
                
                # Check if we're past the due time
                now = datetime.utcnow()
                if now > due_time:
                    print(f"Task {task_id} is now past due. Due: {due_time.isoformat()}, Now: {now.isoformat()}")
                    # Task is past due, send final reminder
                    await self.send_past_due_reminder(user, task)
                    break
                
                # Send the next reminder with increased urgency
                await self.send_reminder(user, task, i + 1)
            
        except Exception as e:
            print(f"Error in reminder sequence for task {task_id}: {str(e)}")
        
        finally:
            # Remove from active reminders when done
            if task_id in self.active_reminders:
                del self.active_reminders[task_id]
    
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
    
    async def send_reminder(self, user, task, urgency_level):
        """
        Send a reminder message with appropriate urgency level using AI
        """
        try:
            description = task['description']
            due_time = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
            
            # Current time in UTC
            now_utc = datetime.utcnow()
            time_left = due_time - now_utc
            minutes_left = max(0, int(time_left.total_seconds() / 60))
            seconds_left = max(0, int(time_left.total_seconds()) % 60)
            
            # Convert UTC due time to New York time for display
            due_time_ny = utc_to_ny(due_time)
            
            # Format the times for display
            due_time_ny_str = format_datetime(due_time_ny, True)
            
            # Format time remaining
            time_remaining = f"{minutes_left} minutes and {seconds_left} seconds"
            
            # Generate AI reminder message with increasing urgency
            ai_message = await self.accountability_partner.generate_reminder_message(
                task_description=description,
                time_remaining=time_remaining,
                urgency_level=urgency_level,
                due_time_local=due_time_ny_str
            )
            
            # Send the AI-generated message
            await user.send(ai_message)
            
            # For higher urgency levels, send additional messages
            if urgency_level >= 5:
                await asyncio.sleep(1)  # Wait a second
                additional_message = await self.accountability_partner.generate_urgent_message(
                    task_description=description,
                    time_remaining=time_remaining,
                    due_time_local=due_time_ny_str
                )
                await user.send(additional_message)
            
            print(f"Sent level {urgency_level} reminder to {user.name} for task {task['id']}")
            
        except Exception as e:
            print(f"Error sending reminder: {str(e)}")
    
    async def send_past_due_reminder(self, user, task):
        """
        Send a reminder for a task that is past due using AI
        """
        try:
            description = task['description']
            due_time = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
            
            # Convert UTC due time to New York time for display
            due_time_ny = utc_to_ny(due_time)
            
            # Format the times for display
            due_time_ny_str = format_datetime(due_time_ny, True)
            
            # Generate AI past due message
            ai_message = await self.accountability_partner.generate_past_due_message(
                task_description=description,
                due_time_local=due_time_ny_str
            )
            
            await user.send(ai_message)
            await asyncio.sleep(1)
            await user.send("⚠️ **LAST CHANCE TO SUBMIT YOUR PROOF!** ⚠️")
            await asyncio.sleep(1)
            await user.send("📸 **SEND AN IMAGE NOW OR LOSE POINTS!** 📸")
            
            print(f"Sent past due reminder to {user.name} for task {task['id']}")
            
        except Exception as e:
            print(f"Error sending past due reminder: {str(e)}") 