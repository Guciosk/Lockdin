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
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.tasks = []
        
    def calculate_urgency_level(self, due_date):
        """Calculate urgency level based on due date proximity"""
        now = datetime.now()
        due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        time_left = due_datetime - now
        
        if time_left.total_seconds() < 0:
            return 5  # Past due
        elif time_left < timedelta(hours=24):
            return 4  # Less than 24 hours
        elif time_left < timedelta(days=3):
            return 3  # Less than 3 days
        elif time_left < timedelta(days=7):
            return 2  # Less than a week
        else:
            return 1  # More than a week
            
    def get_mood_prompt(self, urgency_level):
        """Get AI mood based on urgency level"""
        moods = {
            1: "Be encouraging and supportive",
            2: "Be gently reminding and slightly concerned",
            3: "Be stern and express worry about the deadline",
            4: "Be very assertive and express urgency",
            5: "Be passive-aggressive and disappointed"
        }
        return moods.get(urgency_level, "Be neutral")
        
    async def analyze_task_completion(self, task_description, submitted_notes, image_analysis):
        """Analyze if submitted work matches task requirements"""
        try:
            response = self.client.chat.completions.create(
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
            response = self.client.chat.completions.create(
                model="gpt-4",
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
    
    