import os
import supabase
from datetime import datetime



'''

when image is sent,
bot looks through users table 
and queries the user whose discord_user_id matches
the discord user id of the sender of the image. when it finds that user,
it extracts the user_id from it.
now that it has the user_id, 
it looks through tasks table and queries the task whose user_id matches the user_id the bot got. 
if it cant find the task, the bot responds saying "You don't have any active tasks. Please create a task first."

'''



class ImageStore:
    def __init__(self):
        self.supabase = supabase.create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

    async def store_message(self, user_id: str, username: str = None, message_content: str = "", has_image: bool = False, image_url: str = None, task_id: str = None):
        """
        Store a message in the Supabase feed table
        """
        try:
            data = {
                'user_id': user_id,
                'task_id': task_id,
                'image_url': image_url,
                'post_content': message_content,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            result = self.supabase.table('feed').insert(data).execute()
            return result.data
        except Exception as e:
            print(f"Error storing message in Supabase: {str(e)}")
            return None

    async def store_image(self, image_data: bytes, filename: str):
        """
        Store an image in Supabase storage
        """
        try:
            # First, check if the bucket exists by listing files
            try:
                self.supabase.storage.from_('notes').list()
            except Exception as e:
                print(f"Error accessing notes bucket: {str(e)}")
                print("Attempting to create or access the bucket differently...")
                
                # Try to create the bucket if it doesn't exist
                try:
                    # This might not work depending on permissions, but worth a try
                    self.supabase.storage.create_bucket('notes', {'public': True})
                    print("Created notes bucket successfully")
                except Exception as create_error:
                    print(f"Could not create notes bucket: {str(create_error)}")
                    # If we can't create or access the bucket, we'll store the image URL in the feed table
                    # but return a placeholder URL
                    return "https://placeholder.com/image-not-stored"
            
            # Store the image in the notes bucket
            result = self.supabase.storage.from_('notes').upload(
                path=filename,
                file=image_data,
                file_options={"content-type": "image/png"}
            )
            
            # Get the public URL for the uploaded image
            image_url = self.supabase.storage.from_('notes').get_public_url(filename)
            return image_url
        except Exception as e:
            print(f"Error storing image in Supabase: {str(e)}")
            # Return a placeholder URL so the process can continue
            return "https://placeholder.com/image-upload-failed"

    async def get_user_messages(self, user_id: str, limit: int = 10):
        """
        Retrieve messages for a specific user from the feed table
        """
        try:
            result = self.supabase.table('feed')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error retrieving messages from Supabase: {str(e)}")
            return []
    
    async def find_task_by_user_id(self, discord_user_id: str):
        """
        Retrieve a task from the tasks table by user_id
        """
        try:
            # Get the user by discord_user_id
            user_result = self.supabase.table('users').select('*').eq('discord_user_id', discord_user_id).execute()
            
            # Check if user exists
            if not user_result.data or len(user_result.data) == 0:
                print(f"No user found with discord_user_id: {discord_user_id}")
                return []
            
            user_id = user_result.data[0]['id'] 
            
            # Get tasks for the user
            task_result = self.supabase.table('tasks').select('*').eq('user_id', user_id).execute()
            return task_result.data
        except Exception as e:
            print(f"Error retrieving task from Supabase: {str(e)}")
            return []

    

    async def get_user_tasks(self, discord_user_id: str):
        """
        Retrieve all tasks for a specific user
        """
        try:
            # First, get the user by discord_user_id
            user_result = self.supabase.table('users').select('*').eq('discord_user_id', discord_user_id).execute()
            
            # Check if user exists
            if not user_result.data or len(user_result.data) == 0:
                print(f"No user found with discord_user_id: {discord_user_id}")
                return []
            
            user_id = user_result.data[0]['id']
            
            # Get tasks for the user
            task_result = self.supabase.table('tasks')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('due_time', desc=True)\
                .execute()
            return task_result.data
        except Exception as e:
            print(f"Error retrieving user tasks from Supabase: {str(e)}")
            return []

    async def update_task_status(self, task_id, status, confidence=None, completion=None):
        """
        Update the status of a task in the database
        
        Status can be one of:
        - 'active': Task is active and pending completion
        - 'completed': Task has been completed
        - 'failed': Task was not completed by the due date
        """
        try:
            data = {
                'status': status
            }
            if confidence is not None:
                data['confidence_score'] = confidence
            # Remove the completion_score field as it doesn't exist in the database schema
            # if completion is not None:
            #     data['completion_score'] = completion

            result = self.supabase.table('tasks')\
                .update(data)\
                .eq('id', task_id)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error updating task status in Supabase: {str(e)}")
            return None
        
    async def check_image_exists(self, filename: str):
        """
        Check if an image exists in the notes storage bucket
        """
        try:
            # Try to list files in the bucket to see if the file exists
            files = self.supabase.storage.from_('notes').list()
            
            # Check if the filename is in the list of files
            for file in files:
                if file.get('name') == filename:
                    return True
                    
            return False
        except Exception as e:
            print(f"Error checking if image exists: {str(e)}")
            # Assume the image doesn't exist if we can't check
            return False
            
    async def check_task_has_image(self, task_id: str):
        """
        Check if a task has an associated image in the feed table and if the task is completed
        
        Returns True only if:
        1. There's a feed entry with an image_url for this task, AND
        2. The task status is 'completed'
        
        This allows users to submit another image if their previous submission was unsuccessful.
        """
        try:
            # First, check the task status
            task_result = self.supabase.table('tasks')\
                .select('status')\
                .eq('id', task_id)\
                .execute()
            
            # If the task is already completed, return True (no need for another submission)
            if task_result.data and len(task_result.data) > 0 and task_result.data[0]['status'] == 'completed':
                print(f"Task {task_id} is already completed, no need for another submission")
                return True
            
            # If the task is not completed, check if there's a feed entry with an image_url
            # but return False to allow another submission
            feed_result = self.supabase.table('feed')\
                .select('image_url, status')\
                .eq('task_id', task_id)\
                .not_.is_('image_url', 'null')\
                .execute()
            
            # If there's a feed entry with a completed status, return True
            if feed_result.data and len(feed_result.data) > 0:
                for entry in feed_result.data:
                    if entry.get('status') == 'completed':
                        print(f"Task {task_id} has a completed feed entry, no need for another submission")
                        return True
                
                # If we get here, there are feed entries with images, but none are completed
                print(f"Task {task_id} has {len(feed_result.data)} image submissions, but none are completed. Allowing another submission.")
                return False
            
            # No feed entries with images
            return False
        except Exception as e:
            print(f"Error checking if task has image: {str(e)}")
            return False
        
