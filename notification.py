import smtplib
from email.mime.text import MIMEText
import requests
import os
from dotenv import load_dotenv
# first we will add the email part 

load_dotenv()
def send_notification(subject, notification):
    
    try:
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        receiver = os.getenv("EMAIL_RECEIVER")


        # create message
        msg = MIMEText(f"{notification}")
        msg["Subject"]=subject
        msg["From"]= f"Basharath <{sender}>"
        msg["To"]= receiver


        #connect to the Gmail SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() #start TLS encrytion
            server.login(sender, password)
            server.send_message(msg)
            
        print("Email sent Successfully!")
        
    except Exception as e:
        print("Error Occured",e)

def slack_notification(message):
    try:
        webhook_url = os.getenv("SLACK_WEBHOOK")
        
        message = {"text": message, "username": "Contract Compliance Bot"}
        requests.post(webhook_url, json=message)
    except Exception as e:
        print("Error Occured in Slack Notification", e)

slack_notification("Test Slack Notification from Contract Compliance Bot")