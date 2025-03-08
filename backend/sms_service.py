from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(to_phone_number: int, body: str):
    """
    Sends an SMS using Twilio's API.

    :param to_phone_number: Phone number to send the SMS to
    :param body: The body content of the SMS
    :return: The response from Twilio's API (message SID, etc.)
    """
    message = client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=to_phone_number
    )
    print(f"message.sid: {message.sid}")
    return message.sid