import discord
from datetime import datetime, timedelta
import asyncio
import os
from typing import Dict, List, Optional

class TaskReminder:
    def __init__(self, bot, image_store):
        self.bot = bot
        self.image_store = image_store
        self.reminder_intervals = [1, 2, 3, 4, 5]  # Minutes between reminders
        self.active_reminders = {}  # Dictionary to track active reminders by task_id
        
    async def check_upcoming_tasks(self):
        """
        Periodically check for tasks that are due within 5 minutes
        """
        while True:
            try:
                # Get current time in UTC
                now = datetime.utcnow()
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
                
                # Process each upcoming task
                for task in upcoming_tasks:
                    task_id = task['id']
                    
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
                    if not discord_user_id or task_id in self.active_reminders:
                        continue
                    
                    # Start a reminder sequence for this task
                    asyncio.create_task(self.start_reminder_sequence(task, discord_user_id))
                
                # Check every 60 seconds
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Error checking upcoming tasks: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before trying again
    
    async def start_reminder_sequence(self, task, discord_user_id):
        """
        Start a sequence of increasingly urgent reminders for a task
        """
        task_id = task['id']
        description = task['description']
        due_time = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
        
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
                
                # Wait for the specified interval
                await asyncio.sleep(interval * 60)  # Convert minutes to seconds
                
                # Check again if task is still pending
                task_status = await self.check_task_status(task_id)
                if task_status != 'pending':
                    print(f"Task {task_id} is no longer pending. Stopping reminders.")
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
        Send a reminder message with appropriate urgency level
        """
        try:
            description = task['description']
            due_time = datetime.fromisoformat(task['due_time'].replace('Z', '+00:00'))
            time_left = due_time - datetime.utcnow()
            minutes_left = max(0, int(time_left.total_seconds() / 60))
            
            # Create messages with increasing urgency
            messages = [
                f"🔔 **Friendly Reminder**\nYour task \"{description}\" is due in {minutes_left} minutes!",
                f"⏰ **Task Due Soon**\nYour task \"{description}\" is due in {minutes_left} minutes! Please complete it soon.",
                f"⚠️ **Urgent Reminder**\nYour task \"{description}\" is due in {minutes_left} minutes! Time is running out!",
                f"🚨 **VERY URGENT**\nYour task \"{description}\" is due in {minutes_left} minutes! Complete it NOW!",
                f"🔥 **FINAL WARNING**\nYour task \"{description}\" is due in {minutes_left} minutes! This is your LAST CHANCE!"
            ]
            
            # Select message based on urgency level (capped at the highest level)
            message_index = min(urgency_level, len(messages) - 1)
            message = messages[message_index]
            
            # Send the message
            await user.send(message)
            
            print(f"Sent level {urgency_level} reminder to {user.name} for task {task['id']}")
            
        except Exception as e:
            print(f"Error sending reminder: {str(e)}") 