import json
import os

from typing import Any, Callable

import mesop.labs as mel


@mel.web_component(path="./firebase_auth_component.js")
def firebase_auth_component(on_auth_changed: Callable[[mel.WebEvent], Any]):
    firebase_cfg = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID'),
        "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID')
    }
    firebase_cfg_json = json.dumps(firebase_cfg)
    return mel.insert_web_component(
        name="firebase-auth-component",
        properties={
            "firebaseConfig": firebase_cfg_json
        },
        events={
            "authChanged": on_auth_changed,
        },
    )
