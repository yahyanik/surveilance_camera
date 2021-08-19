
import smtplib
import ssl
from providers import PROVIDERS
from configparser import ConfigParser
import pathlib
import os


keyword = "email-credents" if os.name == 'nt' else "rasp-email-credents"


def get_config():
    path = pathlib.Path("config.cfg")
    cred = ConfigParser()
    cred.read(path)
    return cred


config = get_config()


class sms:

    numbers = ["6074442611"]
    provider = "google"
    sender_credentials = config[keyword].get("email"), config[keyword].get("password")
    receiver_email_addrs = config[keyword].get("receiver_email_addrs")
    subject = "House Camera Module Notice"
    smtp_server = "smtp.gmail.com"
    smtp_port = 465


    @staticmethod
    def send(payload="hello world"):
        sender_email, email_password = sms.sender_credentials
        receiver_email = f"{sms.numbers[0]}@{PROVIDERS[sms.provider].get('sms')}"

        email_msg = f"Subject: {sms.subject}\n To:{receiver_email}\n {payload}"

        # with smtplib.SMTP_SSL(sms.smtp_server, sms.smtp_port, context=ssl.create_default_context()) as email:
         #   email.login(sender_email, email_password)
         #   email.sendmail(sender_email, receiver_email, email_msg)

        with smtplib.SMTP_SSL(sms.smtp_server, sms.smtp_port, context=ssl.create_default_context()) as email:
            email.login(sender_email, email_password)
            email.sendmail(sender_email, sms.receiver_email_addrs, email_msg)


if __name__ == "__main__":
    sms.send()
