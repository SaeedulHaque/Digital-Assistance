import os
import email
from email.policy import default
from pathlib import Path
from bs4 import BeautifulSoup

class EmailTester:
    def __init__(self):
        # WSL/Docker-friendly paths
        self.test_emails_dir = Path('/usr/src/app/test_emails')
        self.attachments_dir = Path('/usr/src/app/attachments')
        self.setup_dirs()
        
        # Create sample emails if none exist
        if not list(self.test_emails_dir.glob('*.eml')):
            self.create_sample_emails()

    def setup_dirs(self):
        """Create required directories"""
        self.test_emails_dir.mkdir(exist_ok=True)
        self.attachments_dir.mkdir(exist_ok=True)

    def create_sample_emails(self):
        """Generate test emails"""
        samples = [
            {
                'sender': 'test1@example.com',
                'recipient': 'you@example.com',
                'subject': 'Test Email with Attachment',
                'body': 'This contains a text attachment',
                'attachment': ('report.txt', b'Sample attachment content')
            },
            {
                'sender': 'test2@example.com',
                'recipient': 'team@example.com',
                'subject': 'HTML Email',
                'body': '<html><body><h1>Header</h1><p>Paragraph</p></body></html>'
            }
        ]

        for i, sample in enumerate(samples, 1):
            msg = email.message.EmailMessage()
            msg['From'] = sample['sender']
            msg['To'] = sample['recipient']
            msg['Subject'] = sample['subject']
            
            if sample['body'].startswith('<html>'):
                msg.add_alternative(sample['body'], subtype='html')
            else:
                msg.set_content(sample['body'])
            
            if 'attachment' in sample:
                msg.add_attachment(
                    sample['attachment'][1],
                    filename=sample['attachment'][0]
                )
            
            with open(self.test_emails_dir / f'test{i}.eml', 'wb') as f:
                f.write(msg.as_bytes())

    def process_emails(self):
        """Process all test emails"""
        for eml_file in self.test_emails_dir.glob('*.eml'):
            with open(eml_file, 'rb') as f:
                yield self.parse_email(f.read())

    def parse_email(self, msg_bytes):
        """Parse email components"""
        msg = email.message_from_bytes(msg_bytes, policy=default)
        
        return {
            'sender': msg['from'],
            'recipient': msg['to'],
            'subject': msg['subject'],
            'body': self.extract_body(msg),
            'attachments': self.save_attachments(msg)
        }

    def extract_body(self, msg):
        """Extract text content"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    return part.get_payload(decode=True).decode()
                if part.get_content_type() == 'text/html':
                    html = part.get_payload(decode=True).decode()
                    return BeautifulSoup(html, 'html.parser').get_text('\n')
        return msg.get_payload(decode=True).decode()

    def save_attachments(self, msg):
        """Save attachments with WSL path handling"""
        saved_files = []
        for part in msg.walk():
            if part.get_filename() and part.get_content_disposition() == 'attachment':
                filepath = self.attachments_dir / Path(part.get_filename()).name
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                saved_files.append(str(filepath))
        return saved_files

if __name__ == '__main__':
    tester = EmailTester()
    for idx, email in enumerate(tester.process_emails(), 1):
        print(f"\nEmail {idx}:")
        print(f"From: {email['sender']}")
        print(f"To: {email['recipient']}")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body'][:100]}...")
        print(f"Attachments: {email['attachments']}")