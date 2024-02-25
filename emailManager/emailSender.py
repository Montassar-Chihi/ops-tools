# import libraries
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_all_emails(all_3pls,emails_3pls,messages):

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        sender_email = "montassar.chihi@glovoapp.com"
        sender_password = "gajf yyhg eqey jwzv"  # for personal account (mc...) "crow bslo masr oulu"
        server.login(sender_email, sender_password)
        SCOPES = [
            "https://www.googleapis.com/auth/gmail.send"
        ]
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        service = build('gmail', 'v1', credentials=creds)

        for current_3pl in list(all_3pls.keys()):
            recipient_email = emails_3pls[current_3pl]
            #         recipient_email = "mc.montassar.chihi@gmail.com"

            filename = messages[current_3pl]["file"]
            message = MIMEMultipart()
            message['Subject'] = messages[current_3pl]["subject"]
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Cc'] = "ops-tn@glovoapp.com"
            html_part = MIMEText(messages[current_3pl]["body"], "html")
            message.attach(html_part)
            with open(filename, "rb") as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=str(filename))
            message.attach(attach)
            server.sendmail(sender_email, "ops-tn@glovoapp.com", message.as_string())
            server.sendmail(sender_email, recipient_email, message.as_string())