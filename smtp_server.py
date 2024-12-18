import asyncio
from aiosmtpd.controller import Controller
import smtplib
from email.message import EmailMessage
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///base.db")

class CustomMessageHandler:
    async def handle_DATA(self, server, session, envelope):
        print('Message received from:', envelope.mail_from)
        print('Message received for:', envelope.rcpt_tos)
        print('Message data:\n')
        print(envelope.content.decode('utf8', errors='replace'))
        print('End of message data')
        return '250 OK'

def send_email(sender, recipient, subject, body):
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)
    
    # Send the email
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('your_username', 'your_password')
        server.send_message(msg)
    
    # Log the email in the database
    db.execute("""
        INSERT INTO email (sender_email, recipient_email, subject, body)
        VALUES (?, ?, ?, ?)
    """, sender, recipient, subject, body)

if __name__ == '__main__':
    controller = Controller(CustomMessageHandler(), hostname='localhost', port=1025)
    print("SMTP server started at localhost:1025")
    controller.start()
    
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()