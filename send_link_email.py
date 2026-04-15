import getpass
import os
import smtplib
from email.message import EmailMessage


def ask(prompt_text, default=None):
    if default:
        value = input(f"{prompt_text} [{default}]: ").strip()
        return value or default
    return input(f"{prompt_text}: ").strip()


def parse_recipients(raw_value):
    recipients = [item.strip() for item in raw_value.split(",")]
    return [email for email in recipients if email]


def build_message(sender, recipient, subject, link):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(f"Hi,\n\nHere is the link you asked for:\n{link}\n")
    message.add_alternative(
        f"""\
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #222;">
    <p>Hi,</p>
    <p>Here is the link you asked for:</p>
    <p><a href="{link}">{link}</a></p>
  </body>
</html>
""",
        subtype="html",
    )
    return message


def main():
    smtp_host = ask("SMTP host", os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port = int(ask("SMTP port", os.getenv("SMTP_PORT", "587")))
    smtp_user = ask("SMTP username", os.getenv("SMTP_USER", ""))
    smtp_password = os.getenv("SMTP_PASSWORD") or getpass.getpass("SMTP password: ")
    sender_email = ask("From email", smtp_user)
    recipients = parse_recipients(ask("Recipient emails (comma-separated)"))
    link = ask("Link to send")
    subject = ask("Subject", "A link for you")

    if not recipients:
        raise SystemExit("No recipient emails provided.")

    use_ssl = smtp_port == 465

    if use_ssl:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
    else:
        server = smtplib.SMTP(smtp_host, smtp_port)

    try:
        server.ehlo()
        if not use_ssl:
            server.starttls()
            server.ehlo()
        server.login(smtp_user, smtp_password)

        for recipient in recipients:
            message = build_message(sender_email, recipient, subject, link)
            server.send_message(message)
            print(f"Sent to {recipient}")
    finally:
        server.quit()


if __name__ == "__main__":
    main()