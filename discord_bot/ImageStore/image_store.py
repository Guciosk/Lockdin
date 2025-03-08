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
if it cant find the task, the bot responds saying “You don't have any active tasks. Please create a task first.”

'''



class ImageStore:
    def __init__(self):
        self.supabase = supabase.create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

    async def store_message(self, user_id: str, username: str, mloessage_content: str, has_image: bool = False, image_url: str = None, task_id: str = None):
        """
        Store a message in the Supabase notes bucket
        """
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'content': message_content,
                'timestamp': datetime.utcnow().isoformat(),
                'has_image': has_image,
                'image_url': image_url,
                'task_id': task_id
            }
            
            result = self.supabase.table('notes').insert(data).execute()
            return result.data
        except Exception as e:
            print(f"Error storing message in Supabase: {str(e)}")
            return None

    async def store_image(self, image_data: bytes, filename: str):
        """
        Store an image in Supabase storage
        """
        try:
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
            return None

    async def get_user_messages(self, user_id: str, limit: int = 10):
        """
        Retrieve messages for a specific user
        """
        try:
            result = self.supabase.table('notes')\
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
            user = self.supabase.table('users').select('*').eq('discord_user_id', discord_user_id).execute()
            user_id = user.data[0]['id'] 
            result = self.supabase.table('tasks').select('*').eq('user_id', user_id).execute()
            return result.data
        except Exception as e:
            print(f"Error retrieving task from Supabase: {str(e)}")
            return None

    

    async def get_user_tasks(self, user_id: str):
        """
        Retrieve all tasks for a specific user
        """
        try:
            result = self.supabase.table('tasks')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('due_time', desc=True)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error retrieving user tasks from Supabase: {str(e)}")
            return []

    async def update_task_status(self, task_id: str, status: str, confidence: float = None, completion: float = None):
        """
        Update task status and scores
        """
        try:
            data = {
                'status': status,
                'last_updated': datetime.utcnow().isoformat()
            }
            if confidence is not None:
                data['confidence_score'] = confidence
            if completion is not None:
                data['completion_score'] = completion

            result = self.supabase.table('tasks')\
                .update(data)\
                .eq('id', task_id)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error updating task status in Supabase: {str(e)}")
            return None
        
