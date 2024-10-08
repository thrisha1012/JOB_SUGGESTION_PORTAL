import os
from flask import Flask
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

@app.route('/')
def send_email():
    message = Mail(
        from_email='sudhubalu04@gmail.com',
        to_emails='thrishala1012@gmail.com',
        subject='Sending with SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return 'Email sent!'
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
