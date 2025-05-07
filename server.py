from flask import Flask, request
from pywebpush import webpush
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
subscriptions = []

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_CLAIMS = {"sub": "mailto:your-email@example.com"}

@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscription = request.json
    subscriptions.append(subscription)
    return '', 201

@app.route('/send_notification', methods=['POST'])
def send_notification():
    message = request.json
    for sub in subscriptions:
        try:
            webpush(
                subscription_info=sub,
                data=json.dumps(message),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except Exception as e:
            print(f"Error sending notification: {e}")
    return '', 200

if __name__ == '__main__':
    app.run(port=5000)