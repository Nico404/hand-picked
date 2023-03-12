import requests
from flask import current_app


def send_simple_message(subject, email, message):
    return requests.post(
        "https://api.mailgun.net/v3/"
        + current_app.config["MAILGUN_DOMAIN"]
        + ".mailgun.org/messages",
        auth=("api", current_app.config["MAILGUN_API_KEY"]),
        data={
            "from": email,
            "to": [
                "nicolas.geron@gmail.com",
            ],
            "subject": subject,
            "text": message,
        },
    )
