from flask import Flask,render_template, request,redirect
import csv
from email.message import EmailMessage
import smtplib
from twilio.rest import Client
import json



app = Flask(__name__)

@app.route('/')
def my_home():
    return render_template('index.html')


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


def write_to_database(data):
    try:
        with open('database.csv',newline= '',mode='a') as database:
            email = data['email']
            subject = data['subject']
            msg = data['message']
            csv_writer = csv.writer(database, delimiter=',',
                                quotechar=' ', quoting=csv.QUOTE_MINIMAL)    
            csv_writer.writerow( [email,subject,msg] )
    except:
        return 'not saved in database'    


def send_sms(contact):
    with open('./config.json') as config_file:
        try:
            config_data = json.load(config_file)
            account_sid = config_data.get("twilio_sid")
            auth_token = config_data.get("twilio_token")
            twilio_number = config_data.get("twilio_number")
            my_phone = config_data.get("notifications_ph")

        except json.JSONDecodeError as json_error:
            raise ValueError(f'Error decoding JSON in config file: {json_error}')
        client = Client(account_sid,auth_token)
        client.messages.create(
        from_= twilio_number,
        body = f'{contact} contacted you, via portfolio website... Check database',
        to = my_phone
        )


def set_email_content(email,about):
    user = email.split("@")[0]
    name = "".join(char for char in user if char.isalpha())
    about_text = f" about \"{about}\" that you indicated me" if about else ""
    content = f"""Hi {name}, thank you for reaching out to me through my portfolio website.\nI appreciate your interest and will do my best to respond promptly as soon as possible{about_text}.\n\nIn the meantime, feel free to explore more of my work on the site.\n\n\nKind regards, Raosari Garcia"""
    return content


def send_email(email_to_contact, subject):
    try:
        email = EmailMessage()
        email['from'] = 'Raosari Garcia'
        email['to'] = email_to_contact
        email['subject'] = 'Thanks for contacting me'
        
        text_email = set_email_content(email_to_contact, subject)
        email.set_content(text_email)

        with open('./config.json') as config_file:
            try:
                config_data = json.load(config_file)
                email_address = config_data.get("email_address")
                app_password = config_data.get("app_password")
            except json.JSONDecodeError as json_error:
                raise ValueError(f'Error decoding JSON in config file: {json_error}')

        with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            try:
                smtp.login(email_address,app_password)
                smtp.send_message(email)
            except smtplib.SMTPAuthenticationError:
                raise ValueError('SMTP Authentication failed. Check email address and app password.')
    except Exception as e:
        return f'Email not sent. Error: {str(e)}'



@app.route('/submit_form', methods=['POST','GET'])
def sumbit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            email = data['email']
            subject = data['subject']

            write_to_database(data)
            send_email(email,subject)
            send_sms(email)
            return redirect('thankyou.html')
        except:
            return 'Not saved, something went wrong'
    else:
        return 'something went wrong'
