import firebase_admin
from firebase_admin import auth, credentials

import mesop as me
import mesop.labs as mel

from firebase_auth_component import (
    firebase_auth_component,
)

# Avoid re-initializing firebase app (useful for avoiding warning message because of hot reloads).
if firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
    cred = credentials.Certificate("secrets/serviceAccountKey.json")
    default_app = firebase_admin.initialize_app(cred)


@me.page(
    path="/hello_world",
    stylesheets=[
        "https://www.gstatic.com/firebasejs/ui/6.1.0/firebase-ui-auth.css"
    ],
    # Loosen the security policy so the firebase JS libraries work.
    security_policy=me.SecurityPolicy(
        dangerously_disable_trusted_types=True,
        allowed_connect_srcs=["*.googleapis.com"],
        allowed_script_srcs=[
            "*.google.com",
            "https://www.gstatic.com",
            "https://cdn.jsdelivr.net",
        ],
    ),
)
def page():
    email = me.state(State).email
    display_name = me.state(State).display_name
    if email:
        me.text(f"Welcome, {display_name}!")
    else:
        me.text("Please sign in!")
    firebase_auth_component(on_auth_changed=on_auth_changed)


@me.stateclass
class State:
    email: str
    display_name: str


def on_auth_changed(e: mel.WebEvent):
    firebaseAuthToken = e.value
    if not firebaseAuthToken:
        me.state(State).email = ""
        me.state(State).display_name = ""
        return

    decoded_token = auth.verify_id_token(firebaseAuthToken)
    if decoded_token["email_verified"] != True:
        me.state(State).email = ""
        me.state(State).display_name = ""
        return

    me.state(State).email = decoded_token["email"]
    me.state(State).display_name = decoded_token["name"]
