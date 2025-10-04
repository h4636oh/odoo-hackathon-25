import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    # IMPORTANT: Replace with your actual email and app password
    sender_email = "priyankaspm04@gmail.com"
    app_password = "dfdj bvra pohw triq " # Replace with your app password

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, app_password)
            smtp_server.sendmail(sender_email, to_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
