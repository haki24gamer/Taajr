import asyncio
from aiosmtpd.controller import Controller
import sqlite3

class CustomMessageHandler:
    async def handle_DATA(self, server, session, envelope):
        sender = envelope.mail_from
        recipient = ', '.join(envelope.rcpt_tos)
        message_data = envelope.content.decode('utf8', errors='replace')
        
        # Extract subject from message data
        subject = ""
        for line in message_data.split('\n'):
            if line.lower().startswith("subject:"):
                subject = line[8:].strip()
                break
        
        # Store email in the database
        conn = sqlite3.connect('/home/haki/Documents/VScode/Projets/Taajr/base.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO email (sender, recipient, subject, message)
            VALUES (?, ?, ?, ?)
        """, (sender, recipient, subject, message_data))
        conn.commit()
        conn.close()
        
        print('Message received from:', sender)
        print('Message received for:', recipient)
        print('Message data:\n')
        print(message_data)
        print('End of message data')
        return '250 OK'

if __name__ == '__main__':
    controller = Controller(CustomMessageHandler(), hostname='localhost', port=1025)
    print("SMTP server started at localhost:1025")
    controller.start()
    
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()