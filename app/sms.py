from threading import Thread
from flask import current_app
from . import sms_client


def send_async_otp(app, to):
    with app.app_context():
        try:
            verification = sms_client.verify.v2.services(
                current_app.config.get("TWILIO_SERVICE_SID")
            ).verifications.create(to=f"+84{to}", channel="sms")
            print(verification.sid)
            print(verification.status)
        except Exception as e:
            print(f"Twilio Error: {e}")


def send_async_sms(app, to, message):
    with app.app_context():
        try:
            sms_client.messages.create(
                body=message,
                from_=app.config.get("TWILIO_NUMBER"),
                to=f"+84{to}",
            )
        except Exception as e:
            print(f"Twilio Error: {e}")


def send_sms(to, message, **kwargs):
    app = current_app._get_current_object()
    thr = Thread(target=send_async_sms, args=[app, to, message])
    thr.start()
    return thr


def send_otp(to, **kwargs):
    app = current_app._get_current_object()
    thr = Thread(target=send_async_otp, args=[app, to])
    thr.start()
    return thr
