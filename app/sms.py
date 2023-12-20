from threading import Thread
from flask import current_app
from . import sms_client


def send_async_sms(app, to, message):
    with app.app_context():
        sms = sms_client.messages.create(
            body=message,
            from_=app.config.get("TWILIO_NUMBER"),
            to=f'+84{to}',
        )
        print(sms)


def send_sms(to, message, **kwargs):
    app = current_app._get_current_object()
    thr = Thread(target=send_async_sms, args=[app, to, message])
    thr.start()
    return thr
