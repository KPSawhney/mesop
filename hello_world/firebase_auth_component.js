import {
  LitElement,
  html,
} from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

import 'https://www.gstatic.com/firebasejs/10.0.0/firebase-app-compat.js';
import 'https://www.gstatic.com/firebasejs/10.0.0/firebase-auth-compat.js';
import 'https://www.gstatic.com/firebasejs/ui/6.1.0/firebase-ui-auth.js';

class FirebaseAuthComponent extends LitElement {
  static properties = {
    isSignedIn: { type: Boolean },
    authChanged: { type: String },
    firebaseConfig: { type: String }
  };

  constructor() {
    super();
    this.isSignedIn = false;
    this.firebaseConfig = '';
  }

  createRenderRoot() {
    // Render in light DOM so firebase-ui-auth works.
    return this;
  }

  initializeFirebase() {
    firebase.initializeApp(this.firebaseConfig);

    var uiConfig = {
      signInSuccessUrl: '/hello_world',
      signInOptions: [firebase.auth.GoogleAuthProvider.PROVIDER_ID],
      signInFlow: "popup",  // Smoother UX.
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());

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

  firstUpdated() {
    const firebaseConfigAttr = this.firebaseConfig;
    if (firebaseConfigAttr) {
      this.firebaseConfig = JSON.parse(firebaseConfigAttr);
      this.initializeFirebase();
    }
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