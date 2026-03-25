import smtplib
from email.message import EmailMessage

class Notification:
    def __init__(self):
        self.sender_email_addr = "cosc310tag@gmail.com"
        self.email_pass = "jake xskl krez frbw"
        self.session = None

    def _connect(self):
        self.session = smtplib.SMTP('smtp.gmail.com', 587)
        self.session.starttls()
        self.session.login(self.sender_email_addr, self.email_pass)

    def send_notification(self, subject: str, message: str, receiver_email: str):
        self._connect()
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = subject
        msg['From'] = self.sender_email_addr
        msg['To'] = receiver_email
        return self.session.send_message(msg)