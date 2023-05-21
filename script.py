import os
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import subprocess
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import webbrowser

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

python_files = ["/home/gaurav/ScrapIt/naukri.py","/home/gaurav/ScrapIt/timesjob.py","/home/gaurav/ScrapIt/Indeed.py"]

for file in python_files:
    subprocess.run(['python',file])

def create_gmail_service():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('/home/gaurav/ScrapIt/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)

            if not creds and not creds.valid:
                # Manually open Brave browser
                webbrowser.register('brave', None, webbrowser.GenericBrowser('/usr/bin/brave'))
                webbrowser.get('brave').open(flow.authorization_url())

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message_with_attachment(sender, to, subject, message_text, file_paths):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    message.attach(MIMEText(message_text, 'plain'))

    for file_path in file_paths:
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        with open(file_path, 'rb') as file:
            file_data = file.read()
        file_part = MIMEBase(main_type, sub_type)
        file_part.set_payload(file_data)
        file_part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        message.attach(file_part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def send_email(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message sent successfully.')
    except Exception as e:
        print('An error occurred while sending the email:', str(e))


def main():
    sender = 'gaurav.mishra216rock@gmail.com'
    to = 'gaurav.mishra216rock@gmail.com'
    subject = 'Email Subject'
    message_text = 'Email Body'

    file_paths = ['/home/gaurav/ScrapIt/timesjob.csv', '/home/gaurav/ScrapIt/naukri.csv','/home/gaurav/ScrapIt/cache/Indeed.csv']  # Adjust the file paths accordingly

    service = create_gmail_service()
    message = create_message_with_attachment(sender, to, subject, message_text, file_paths)
    send_email(service, 'me', message)


if __name__ == '__main__':
    main()
