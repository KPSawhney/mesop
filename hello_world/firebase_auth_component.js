import {
  LitElement,
  html,
} from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

import 'https://www.gstatic.com/firebasejs/10.0.0/firebase-app-compat.js';
import 'https://www.gstatic.com/firebasejs/10.0.0/firebase-auth-compat.js';
import 'https://www.gstatic.com/firebasejs/ui/6.1.0/firebase-ui-auth.js';

// TODO: Ensure you have populated these fields in `app.yaml` before deploying.
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
console.log('Firebase initialized');


var uiConfig = {
  signInSuccessUrl: '/hello_world',
  signInOptions: [firebase.auth.GoogleAuthProvider.PROVIDER_ID],
  signInFlow: "popup",
  // TODO: create ToS and privacy policy.
  // // tosUrl and privacyPolicyUrl accept either url string or a callback
  // // function.
  // // Terms of service url/callback.
  // tosUrl: '<your-tos-url>',
  // // Privacy policy url/callback.
  // privacyPolicyUrl: function () {
  //   window.location.assign('<your-privacy-policy-url>');
  // },
};

// Initialize the FirebaseUI Widget using Firebase.
var ui = new firebaseui.auth.AuthUI(firebase.auth());

class FirebaseAuthComponent extends LitElement {
  static properties = {
    isSignedIn: { type: Boolean },
    authChanged: { type: String },
  };

  constructor() {
    super();
    this.isSignedIn = false;
  }

  createRenderRoot() {
    // Render in light DOM so firebase-ui-auth works.
    return this;
  }

  firstUpdated() {
    firebase.auth().onAuthStateChanged(
      async (user) => {
        if (user) {
          this.isSignedIn = true;
          const token = await user.getIdToken();
          this.dispatchEvent(new MesopEvent(this.authChanged, token));
        } else {
          this.isSignedIn = false;
          this.dispatchEvent(new MesopEvent(this.authChanged, ''));
        }
      },
      function (error) {
        console.error('Error getting ID token:', error);
      },
    );
    ui.start('#firebaseui-auth-container', uiConfig);
  }

  signOut() {
    firebase.auth().signOut();
  }

  render() {
    return html`
        <div
          id="firebaseui-auth-container"
          style="${this.isSignedIn ? 'display: none' : ''}"
        ></div>
        <div
          class="firebaseui-container firebaseui-page-provider-sign-in firebaseui-id-page-provider-sign-in firebaseui-use-spinner"
          style="${this.isSignedIn ? '' : 'display: none'}"
        >
          <button
            style="background-color:#ffffff"
            class="firebaseui-idp-button mdl-button mdl-js-button mdl-button--raised firebaseui-idp-google firebaseui-id-idp-button"
            @click="${this.signOut}"
          >
            <span class="firebaseui-idp-text firebaseui-idp-text-long"
              >Sign out</span
            >
          </button>
        </div>
      `;
  }
}

customElements.define('firebase-auth-component', FirebaseAuthComponent);