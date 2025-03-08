import openai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_image(image_url, custom_prompt="Describe the image in detail"):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": custom_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyze_image: {str(e)}")
        return f"Error analyzing image: {str(e)}"

class OpenAI_Accountability_Partner:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.tasks = []
        
    def calculate_urgency_level(self, due_date):
        """
        Calculate the urgency level based on the due date
        """
        try:
            # Parse the due date
            due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            
            # Calculate the time difference
            now = datetime.utcnow()
            time_diff = due_date_obj - now
            
            # Convert to hours
            hours_remaining = time_diff.total_seconds() / 3600
            
            # Determine urgency level
            if hours_remaining <= 1:
                return "EXTREMELY HIGH"
            elif hours_remaining <= 3:
                return "VERY HIGH"
            elif hours_remaining <= 6:
                return "HIGH"
            elif hours_remaining <= 12:
                return "MODERATE"
            elif hours_remaining <= 24:
                return "LOW"
            else:
                return "VERY LOW"
        except Exception as e:
            print(f"Error calculating urgency level: {str(e)}")
            return "UNKNOWN"
    
    def get_mood_prompt(self, urgency_level):
        """
        Get the mood prompt based on the urgency level
        """
        if urgency_level == "EXTREMELY HIGH":
            return "You are an extremely urgent and demanding accountability coach. Use ALL CAPS frequently. Be very direct and forceful."
        elif urgency_level == "VERY HIGH":
            return "You are a very urgent and stern accountability coach. Use some ALL CAPS for emphasis. Be direct and authoritative."
        elif urgency_level == "HIGH":
            return "You are an urgent accountability coach. Be firm and direct, but not overly aggressive."
        elif urgency_level == "MODERATE":
            return "You are a moderately urgent accountability coach. Be encouraging but with a sense of urgency."
        elif urgency_level == "LOW":
            return "You are a gentle but effective accountability coach. Be friendly but clear about the deadline."
        else:
            return "You are a calm and supportive accountability coach. Be encouraging and positive."
    
    async def generate_reminder_message(self, task_description, time_remaining, urgency_level, due_time_local=None):
        """
        Generate a reminder message with appropriate urgency level
        """
        # Map the numeric urgency level to a text level
        urgency_text = "VERY LOW"
        if urgency_level >= 8:
            urgency_text = "EXTREMELY HIGH"
        elif urgency_level >= 6:
            urgency_text = "VERY HIGH"
        elif urgency_level >= 4:
            urgency_text = "HIGH"
        elif urgency_level >= 2:
            urgency_text = "MODERATE"
        elif urgency_level >= 0:
            urgency_text = "LOW"
        
        # Get the mood prompt
        mood_prompt = self.get_mood_prompt(urgency_text)
        
        # Create the system prompt
        system_prompt = f"""
{mood_prompt}

You are reminding the user about their upcoming task deadline. The task is due in {time_remaining}.
Your message should be concise (max 3-4 sentences) and should:
1. Remind them about the task
2. Mention the time remaining
3. Emphasize the importance of submitting an IMAGE as proof
4. Create a sense of urgency appropriate to the time remaining

As the urgency level increases, your tone should become more forceful and urgent.
Urgency level: {urgency_text}

Use appropriate emojis to enhance your message (⏰, ⚠️, 🔥, 🚨, etc.)
"""
        
        # Add local time information if provided
        user_prompt = f"Generate a reminder message for the task: '{task_description}' which is due in {time_remaining}"
        if due_time_local:
            user_prompt += f" (at {due_time_local} New York time)"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating reminder message: {str(e)}")
            # Fallback message if API call fails
            return f"⚠️ **REMINDER** ⚠️\nYour task \"{task_description}\" is due in {time_remaining}! Please submit an image as proof to earn points."
    
    async def generate_urgent_message(self, task_description, time_remaining, due_time_local=None):
        """
        Generate an additional urgent message for high urgency levels
        """
        system_prompt = """
You are an EXTREMELY URGENT and DEMANDING accountability coach. Use ALL CAPS frequently.

Generate a very short (1-2 sentences), extremely urgent follow-up message to remind the user about their task.
The message should be dramatic and create a strong sense of urgency.

Use appropriate emojis to enhance your message (⏰, ⚠️, 🔥, 🚨, etc.)
"""
        
        # Add local time information if provided
        user_prompt = f"Generate an extremely urgent follow-up message for the task: '{task_description}' which is due in {time_remaining}"
        if due_time_local:
            user_prompt += f" (at {due_time_local} New York time)"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating urgent message: {str(e)}")
            # Fallback message if API call fails
            return f"🚨 **URGENT: SUBMIT NOW!** 🚨\nTime is running out for your task: \"{task_description}\"!"
    
    async def generate_past_due_message(self, task_description, due_time_local=None):
        """
        Generate a message for a task that is past due
        """
        system_prompt = """
You are a stern but fair accountability coach dealing with a user who has missed their deadline.

Generate a message that:
1. Informs them that their task is now past due
2. Emphasizes the importance of still submitting an IMAGE as proof IMMEDIATELY
3. Reminds them they will lose points if they don't submit
4. Creates a sense of urgency

Use appropriate emojis to enhance your message (⏱️, ⚠️, 🔥, 🚨, etc.)
"""
        
        # Add local time information if provided
        user_prompt = f"Generate a past due message for the task: '{task_description}' which is now overdue"
        if due_time_local:
            user_prompt += f" (it was due at {due_time_local} New York time)"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating past due message: {str(e)}")
            # Fallback message if API call fails
            return f"⏱️ **TASK PAST DUE!** ⏱️\nYour task \"{task_description}\" is now PAST DUE! Please submit an image as proof IMMEDIATELY to earn points."
    
    async def generate_failure_message(self, task_description, due_date, due_time_local=None):
        """
        Generate a message for a task that has failed (no image submitted by due date)
        """
        system_prompt = """
You are a disappointed but constructive accountability coach.

Generate a message that:
1. Informs the user that they have failed to complete their task on time
2. Expresses disappointment but remains constructive
3. Emphasizes the importance of submitting proof for future tasks
4. Encourages them to do better next time

Use appropriate emojis to enhance your message (❌, 😞, 📝, etc.)
"""
        
        # Add local time information if provided
        user_prompt = f"Generate a failure message for the task: '{task_description}' which was due on {due_date} but no proof was submitted"
        if due_time_local:
            user_prompt += f" (it was due at {due_time_local} New York time)"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating failure message: {str(e)}")
            # Fallback message if API call fails
            return f"❌ **Task Failed!** You didn't submit an image for your task: \"{task_description}\"."
            
    async def analyze_task_completion(self, task_description, submitted_notes, image_analysis):
        """
        Analyze whether the submitted content meets the task criteria
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are a strict task completion analyzer. 
                    Evaluate the submitted work against the task requirements and provide:
                    1. Confidence score (0-100%) of how well the submission matches the task
                    2. Completion score (0-100%) of how thoroughly the task was done
                    3. Brief explanation of your scoring
                    Format: {confidence}|{completion}|{explanation}"""},
                    {"role": "user", "content": f"""
                    Task Description: {task_description}
                    
                    Submitted Notes: {submitted_notes}
                    
                    Image Analysis: {image_analysis}
                    
                    Analyze the submission and provide scores."""}
                ]
            )
            
            analysis = response.choices[0].message.content.split('|')
            confidence = float(analysis[0].strip('%'))
            completion = float(analysis[1].strip('%'))
            explanation = analysis[2].strip()
            
            return confidence, completion, explanation
            
        except Exception as e:
            print(f"Error analyzing task completion: {str(e)}")
            return 0, 0, "Error analyzing submission"

    async def generate_response(self, task_description, due_date, submitted_notes, image_analysis):
        """Generate a response based on task analysis and urgency"""
        try:
            # Calculate urgency level
            urgency_level = self.calculate_urgency_level(due_date)
            mood = self.get_mood_prompt(urgency_level)
            
            # Analyze task completion
            confidence, completion, analysis = await self.analyze_task_completion(
                task_description, submitted_notes, image_analysis
            )
            
            # Generate appropriate response
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"""You are an AI accountability partner. {mood}. 
                    The task is {task_description} due on {due_date}."""},
                    {"role": "user", "content": f"""
                    Analysis Results:
                    - Confidence Match: {confidence}%
                    - Completion Rate: {completion}%
                    - Analysis: {analysis}
                    
                    Generate a response that:
                    1. Acknowledges the submission
                    2. Comments on the quality and completeness
                    3. Provides feedback based on the scores
                    4. Mentions the deadline with appropriate urgency
                    5. Maintains the specified mood"""}
                ]
            )
            
            return {
                'response': response.choices[0].message.content,
                'confidence': confidence,
                'completion': completion,
                'meets_criteria': confidence >= 70 and completion >= 40
            }
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                'response': "Error generating response",
                'confidence': 0,
                'completion': 0,
                'meets_criteria': False
            }
    
    