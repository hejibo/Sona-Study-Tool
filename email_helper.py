import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import data

class GmailClient(object):
    def __init__(self, email, password):
        """Constructor for the Gmail Client Initiates the TLS connection with the
        SMTP server.

        Arguments:
            email (string): the email address associated with the Gmail account.
            password (string): the password associated with the Gmail account.
        """

        self.email = email
        self.password = password
        self.server = 'smtp.gmail.com'
        self.port = 587
        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(self.email, self.password)
        self.session = session
    
    def send_message(self, subject, recipients, text, html):
        """Sends a mass email message (containing both text and HTML parts) to
        the recipients, hiding the list of recipients from each recipient. (The 'To'
        and 'From' fields are set to the sender's email address.)

        Arguments:
            subject (string): the subject line for the email
            recipients (list of str): the recipient email addresses, each represented
                as a string.
            text (string): the text part of the email message
            html (string): the HTML part of the email message. Should be valid HTML.

        This function does not have a return value.
        """
        msg = MIMEMultipart('alternative')
        msg['To'] = self.email
        msg['From'] = self.email
        msg['Subject'] = subject
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        self.session.sendmail(
            self.email,
            recipients,
            msg.as_string(),
            )

    def close(self):
        """Closes the connection with the server."""
        self.session.quit()