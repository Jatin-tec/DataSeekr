import mailbox
import bs4
import weaviate
import os
import json
from dotenv import load_dotenv

load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        # Replace with your inference API key
        "X-HuggingFace-Api-Key": huggingface_api_key
    }
)

def get_html_text(html):
    try:
        return bs4.BeautifulSoup(html, 'lxml').body.get_text(' ', strip=True)
    except AttributeError: # message contents empty
        return None

class GmailMboxMessage():
    def __init__(self, email_data):
        if not isinstance(email_data, mailbox.mboxMessage):
            raise TypeError('Variable must be type mailbox.mboxMessage')
        self.email_data = email_data

    def parse_email(self):
        email_labels = self.email_data['X-Gmail-Labels']
        email_date = self.email_data['Date']
        email_from = self.email_data['From']
        email_to = self.email_data['To']
        email_subject = self.email_data['Subject']
        email_text = self.read_email_payload() 

        return {
            "email_labels": email_labels,
            "email_date": email_date,
            "email_from": email_from,
            "email_to": email_to,
            "email_subject": email_subject,
            "email_text": email_text
        }

    def read_email_payload(self):
        email_payload = self.email_data.get_payload()
        if self.email_data.is_multipart():
            email_messages = list(self._get_email_messages(email_payload))
        else:
            email_messages = [email_payload]
        return [self._read_email_text(msg) for msg in email_messages]

    def _get_email_messages(self, email_payload):
        for msg in email_payload:
            if isinstance(msg, (list,tuple)):
                for submsg in self._get_email_messages(msg):
                    yield submsg
            elif msg.is_multipart():
                for submsg in self._get_email_messages(msg.get_payload()):
                    yield submsg
            else:
                yield msg

    def _read_email_text(self, msg):
        content_type = 'NA' if isinstance(msg, str) else msg.get_content_type()
        encoding = 'NA' if isinstance(msg, str) else msg.get('Content-Transfer-Encoding', 'NA')
        if 'text/plain' in content_type and 'base64' not in encoding:
            msg_text = msg.get_payload()
        elif 'text/html' in content_type and 'base64' not in encoding:
            msg_text = get_html_text(msg.get_payload())
        elif content_type == 'NA':
            msg_text = get_html_text(msg)
        else:
            msg_text = None
        return (content_type, encoding, msg_text)

######################### End of library, example of use below

mbox_obj = mailbox.mbox('data/dump.mbox')

num_entries = len(mbox_obj)

for idx, email_obj in enumerate(mbox_obj):
    if idx > 650:
        email_data = GmailMboxMessage(email_obj)
        email_data.parse_email()
        email_payload = email_data.email_data.get_payload()

        print({str(email_data.parse_email()["email_text"][0][2])})

        # if not ("social" or "promotions") in email_data.parse_email()["email_labels"]:
            # print(email_data.parse_email()["email_labels"])
            # print("Not social")
            # uuid = client.data_object.create({
            #     'MailSubject': str(email_data.parse_email()["email_subject"]),
            #     'MailBody': f"""labels: {str(email_data.parse_email()["email_labels"])}
            #                     from: {str(email_data.parse_email()["email_from"])}
            #                     subject: {str(email_data.parse_email()["email_subject"])}
            #                     body: {str(email_data.parse_email()["email_text"][0][2])}""",
            # }, 'Mails')
            # print(uuid)
        print('Parsing email {0} of {1}'.format(idx, num_entries))
        print("-----------------------------------------")