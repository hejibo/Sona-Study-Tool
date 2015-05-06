import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import data

class Gmail(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.server = 'smtp.gmail.com'
        self.port = 587
        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(self.email, self.password)
        self.session = session
        return None
    
    def send_message(self, subject, recipient, text, html):
        msg = MIMEMultipart('alternative')
        msg['To'] = self.email
        #msg['BCC'] = ", ".join(recipient)
        msg['From'] = self.email
        msg['Subject'] = subject
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        self.session.sendmail(
                              self.email,
                              recipient,
                              msg.as_string())

    def close(self):
        self.session.quit()



#msg = Gmail(data.GMAIL_USERNAME, data.GMAIL_PASSWORD)
#msg.send_message("New SONA Study", data.recipients,"Check out this new study\r\n\r\n \"https://sbe.sona-systems.com/\"", "<html><head></head><body><p>This is a test message.</p><p>Text and HTML</p><p><a href =\"https://sbe.sona-systems.com/\">login here</a></body></html>")
