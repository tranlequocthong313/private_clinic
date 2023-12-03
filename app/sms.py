from . import sms_client
from threading import Thread
from flask import current_app
import os


def send_async_sms(app, to, body):
    with app.app_context():
        message = sms_client.messages.create(
          from_=os.getenv('TWILIO_PHONE'),
          body=body,
          to=to
        )
        print(message)


def send_sms(to, body, **kwargs):
    app = current_app._get_current_object()
    thr = Thread(target=send_async_sms, args=[app, to, body])
    thr.start()
    return thr

