import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart



def send_email(toaddrs, subject, content):
    fromaddr = 'camdroid.usp@gmail.com'

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddrs
    msg['Subject'] = subject

    body = content
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "cam123456")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddrs, text)