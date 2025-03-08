import openai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_image(image_url, custom_prompt="Describe the image in detail"):
    try:
        # Add a timeout for the request to prevent hanging
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
                                "url": image_url,
                                "detail": "low"  # Use low detail to speed up processing
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            timeout=30  # Add a 30-second timeout
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyze_image: {str(e)}")
        # Return a more graceful error message that won't break downstream processing
        return "Unable to analyze image due to download or processing error. Please try again later."

class OpenAI_Accountability_Partner:
    def __init__(self):
        self.conversation_history = {}  # Dictionary to store conversation history by task_id
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.tasks = []
        
    def calculate_urgency_level(self, due_date):
        """
        Calculate urgency level based on time remaining
        """
        try:
            # Parse the due date
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            
            # Calculate time remaining
            now = datetime.utcnow()
            time_remaining = due_date - now
            
            # Convert to hours
            hours_remaining = time_remaining.total_seconds() / 3600
            
            # Determine urgency level
            if hours_remaining <= 0:
                return "EXTREMELY HIGH"
            elif hours_remaining <= 1:
                return "VERY HIGH"
            elif hours_remaining <= 3:
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
    
    def get_mood_prompt(self, urgency_level, reminder_count=0):
        """
        Get the mood prompt based on the urgency level and reminder count
        Gordon Ramsay style - starts nice and gradually becomes more intense
        """
        # Gordon Ramsay progression based on reminder count (0-10)
        if reminder_count == 0:
            return "You are a friendly and supportive accountability coach like Gordon Ramsay in MasterChef Junior. Be encouraging, positive, and gentle. Use supportive language and be very optimistic about the person completing their task."
        elif reminder_count == 1:
            return "You are a slightly more firm accountability coach like Gordon Ramsay in MasterChef. Still friendly but with a hint of urgency. Mention the deadline politely but clearly."
        elif reminder_count == 2:
            return "You are Gordon Ramsay starting to get a bit impatient. Show some concern about the time remaining. Use one or two emphasized words. Be direct but still professional."
        elif reminder_count == 3:
            return "You are Gordon Ramsay getting noticeably frustrated. Use more direct language and occasional ALL CAPS for emphasis. Express clear concern about the deadline approaching. Be more assertive."
        elif reminder_count == 4:
            return "You are Gordon Ramsay getting quite annoyed. Use stronger language and more ALL CAPS. Express frustration about the lack of progress. Use some of Gordon's signature phrases but keep it professional."
        elif reminder_count == 5:
            return "You are Gordon Ramsay getting angry. Use frequent ALL CAPS and exclamation marks. Be very direct and use some of Gordon's milder insults (like 'donkey'). Express serious concern about missing the deadline."
        elif reminder_count == 6:
            return "You are Gordon Ramsay in Hell's Kitchen mode. Use LOTS OF ALL CAPS and Gordon's signature insults. Be dramatic about the time pressure. Use phrases like 'WAKE UP!' and 'MOVE IT!'"
        elif reminder_count == 7:
            return "You are Gordon Ramsay having a meltdown. MOSTLY ALL CAPS. Use Gordon's famous rants and insults. Be extremely dramatic about the deadline. Use phrases like 'IT'S RAW!' and 'WHAT ARE YOU DOING?!'"
        elif reminder_count == 8:
            return "You are Gordon Ramsay at his angriest. ALMOST ENTIRELY IN ALL CAPS. Use Gordon's most intense insults and expressions of disbelief. Act like the situation is a complete disaster."
        elif reminder_count >= 9:
            return "You are Gordon Ramsay at his absolute limit. ENTIRELY IN ALL CAPS. Use Gordon's most extreme reactions and signature phrases. Act like this is the worst situation you've ever seen. Express utter disbelief at the lack of progress."
    
    def initialize_conversation(self, task_id):
        """
        Initialize conversation history for a task
        """
        if task_id not in self.conversation_history:
            self.conversation_history[task_id] = []
    
    def clear_conversation(self, task_id):
        """
        Clear conversation history for a task
        """
        if task_id in self.conversation_history:
            self.conversation_history[task_id] = []
    
    def add_to_conversation(self, task_id, message):
        """
        Add a message to the conversation history
        """
        self.initialize_conversation(task_id)
        self.conversation_history[task_id].append(message)
    
    def get_conversation_history(self, task_id):
        """
        Get the conversation history for a task
        """
        self.initialize_conversation(task_id)
        return self.conversation_history[task_id]
    
    async def generate_reminder_message(self, task_description, time_remaining, urgency_level, due_time_local=None, task_id=None, reminder_count=0):
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
        
        # Get the mood prompt based on the reminder count (Gordon Ramsay progression)
        mood_prompt = self.get_mood_prompt(urgency_text, reminder_count)
        
        # Get conversation history if task_id is provided
        conversation_context = ""
        if task_id:
            history = self.get_conversation_history(task_id)
            if history:
                conversation_context = "Previous messages in this conversation:\n"
                for i, msg in enumerate(history):
                    conversation_context += f"Message {i+1}: {msg}\n"
                conversation_context += "\nContinue the conversation with the same personality, but with increasing urgency and frustration like Gordon Ramsay would. Reference previous messages if appropriate.\n\n"
        
        try:
            # Format the due time string
            due_time_str = f" (due at {due_time_local})" if due_time_local else ""
            
            # Create the prompt
            prompt = f"{mood_prompt}\n\n{conversation_context}The user has a task: \"{task_description}\"{due_time_str}. They have {time_remaining} left to complete it. Remind them to complete their task with the appropriate level of urgency. Be concise and direct. Use Gordon Ramsay's style of communication."
            
            # Generate the response
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Please remind me about my task: {task_description}. I have {time_remaining} left."}
                ],
                max_tokens=150
            )
            
            message = response.choices[0].message.content.strip()
            
            # Add to conversation history if task_id is provided
            if task_id:
                self.add_to_conversation(task_id, message)
            
            return message
            
        except Exception as e:
            print(f"Error generating reminder message: {str(e)}")
            return f"⏰ Reminder: Your task \"{task_description}\" is due soon! You have {time_remaining} left to complete it."
    
    async def generate_urgent_message(self, task_description, time_remaining, due_time_local=None, task_id=None, reminder_count=8):
        """
        Generate an urgent message for tasks that are very close to the deadline
        Uses Gordon Ramsay's angry chef persona
        """
        try:
            # Format the due time string
            due_time_str = f" (due at {due_time_local})" if due_time_local else ""
            
            # Get conversation history if task_id is provided
            conversation_context = ""
            if task_id:
                history = self.get_conversation_history(task_id)
                if history:
                    conversation_context = "Previous messages in this conversation:\n"
                    for i, msg in enumerate(history[-3:]):  # Only use the last 3 messages
                        conversation_context += f"Message {i+1}: {msg}\n"
                    conversation_context += "\nContinue the conversation with the same personality, but with EXTREME urgency and frustration like Gordon Ramsay at his angriest.\n\n"
            
            # Get the mood prompt for a very angry Gordon Ramsay
            mood_prompt = self.get_mood_prompt("EXTREMELY HIGH", reminder_count)
            
            # Create the prompt
            prompt = f"{mood_prompt}\n\n{conversation_context}The user has a task: \"{task_description}\"{due_time_str}. They have ONLY {time_remaining} left to complete it! This is EXTREMELY URGENT! Channel Gordon Ramsay at his most frustrated and angry. Use ALL CAPS liberally. Be dramatic about the time pressure. Use Gordon's signature phrases and insults."
            
            # Generate the response
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"I still haven't completed my task: {task_description}. I only have {time_remaining} left!"}
                ],
                max_tokens=150
            )
            
            message = response.choices[0].message.content.strip()
            
            # Add to conversation history if task_id is provided
            if task_id:
                self.add_to_conversation(task_id, message)
            
            return message
            
        except Exception as e:
            print(f"Error generating urgent message: {str(e)}")
            return f"🚨 **URGENT!!!** 🚨\nYour task \"{task_description}\" is due in {time_remaining}! SUBMIT NOW!!!"
    
    async def generate_past_due_message(self, task_description, due_time_local=None, task_id=None):
        """
        Generate a message for tasks that are past due
        Uses Gordon Ramsay's extremely disappointed and angry chef persona
        """
        try:
            # Format the due time string
            due_time_str = f" (was due at {due_time_local})" if due_time_local else ""
            
            # Get conversation history if task_id is provided
            conversation_context = ""
            if task_id:
                history = self.get_conversation_history(task_id)
                if history:
                    conversation_context = "Previous messages in this conversation:\n"
                    for i, msg in enumerate(history[-3:]):  # Only use the last 3 messages
                        conversation_context += f"Message {i+1}: {msg}\n"
                    conversation_context += "\nContinue the conversation with the same personality, but now the task is PAST DUE. Channel Gordon Ramsay at his most disappointed and angry.\n\n"
            
            # Create the prompt for an extremely angry Gordon Ramsay
            prompt = f"""You are Gordon Ramsay at his absolute angriest and most disappointed. The user has FAILED to complete their task on time. 

{conversation_context}The task: "{task_description}"{due_time_str} is NOW PAST DUE! 

Express extreme disappointment and frustration in Gordon Ramsay's signature style. Use ALL CAPS liberally. Use Gordon's famous insults and expressions of disbelief. Make it clear that they have FAILED to meet the deadline but they STILL NEED TO SUBMIT their work IMMEDIATELY.

Include a reminder that they need to submit an IMAGE as proof of their work, even though it's late."""
            
            # Generate the response
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"My task '{task_description}' is past due now. What should I do?"}
                ],
                max_tokens=200
            )
            
            message = response.choices[0].message.content.strip()
            
            # Add to conversation history if task_id is provided
            if task_id:
                self.add_to_conversation(task_id, message)
            
            return message
            
        except Exception as e:
            print(f"Error generating past due message: {str(e)}")
            return f"⚠️ **TASK PAST DUE!** ⚠️\nYour task \"{task_description}\" is now PAST DUE! Submit your proof IMMEDIATELY to avoid it being marked as failed!"

    async def generate_failure_message(self, task_description, due_date, due_time_local=None, task_id=None):
        """
        Generate a message for tasks that have been marked as failed
        Uses Gordon Ramsay's extremely disappointed chef persona
        """
        try:
            # Format the due time string
            due_time_str = f" (was due at {due_time_local})" if due_time_local else ""
            
            # Get conversation history if task_id is provided
            conversation_context = ""
            if task_id:
                history = self.get_conversation_history(task_id)
                if history:
                    conversation_context = "Previous messages in this conversation:\n"
                    for i, msg in enumerate(history[-3:]):  # Only use the last 3 messages
                        conversation_context += f"Message {i+1}: {msg}\n"
                    conversation_context += "\nContinue the conversation with the same personality, but now the task has been MARKED AS FAILED. Channel Gordon Ramsay at his most disappointed.\n\n"
            
            # Create the prompt for a disappointed Gordon Ramsay
            prompt = f"""You are Gordon Ramsay, extremely disappointed and frustrated. The user has COMPLETELY FAILED to complete their task on time.

{conversation_context}The task: "{task_description}"{due_time_str} has been MARKED AS FAILED because they did not submit it on time.

Express extreme disappointment in Gordon Ramsay's signature style. Use ALL CAPS liberally. Use Gordon's famous insults and expressions of disbelief. Make it clear that they have FAILED and let them know they can reset the task if they still want to complete it.

Remind them that they need to use the command "!reset_task <task_id>" if they want to try again."""
            
            # Generate the response
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"My task '{task_description}' has been marked as failed. What should I do now?"}
                ],
                max_tokens=200
            )
            
            message = response.choices[0].message.content.strip()
            
            # Add to conversation history if task_id is provided
            if task_id:
                self.add_to_conversation(task_id, message)
            
            return message
            
        except Exception as e:
            print(f"Error generating failure message: {str(e)}")
            return f"❌ **TASK FAILED** ❌\nYour task \"{task_description}\" has been marked as FAILED because you did not complete it by the deadline. If you still want to complete this task, use the command: !reset_task <task_id>"
            
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
                'meets_criteria': confidence >= 70 and completion >= 40
            }
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                'response': "Error generating response",
                'confidence': 0,
                'meets_criteria': False
            }
    
    