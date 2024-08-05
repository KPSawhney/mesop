## Firebase Auth with Mesop

### Overview

This project demonstrates a simple web application built with Mesop that leverages Firebase Authentication for user sign-in. Users can sign in with their Google accounts and see a personalized greeting.

### Directory Structure

* **hello_world:** Contains the core application logic.
  * `hello_world.py`: Defines the main page and handles user interactions.
  * `firebase_auth_component.py`: Manages Firebase authentication integration.
* **secrets:** Stores the Firebase service account key (`.gitignore`d for security).
* **JS:** Contains JavaScript components for the frontend.
  * `firebase_auth_component.js`: Implements the Firebase UI component.
* **app.yaml:** Configuration for deploying the app to Google App Engine.
* **requirements.txt:** Lists project dependencies.
* **README.md:** This file.

### Prerequisites

* Python 3.6+
* Google Cloud SDK
* Firebase project with Google Sign-In enabled

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo-url.git
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a Firebase service account key:**
   * Go to your Firebase project's settings.
   * Create a service account key and download it as a JSON file.
   * Place the JSON file in the `secrets` directory.
4. **Set environment variables:**
   * Replace the placeholder values in `app.yaml` with your Firebase project's configuration.

### Deployment

1. **Deploy to Google App Engine:**
   ```bash
   gcloud app deploy
   ```

### How it Works

* The `hello_world.py` file defines the main page and uses the `firebase_auth_component` to handle authentication.
* The `firebase_auth_component` interacts with the Firebase SDK to manage sign-in and sign-out.
* The frontend component (`firebase_auth_component.js`) renders the Firebase UI for user interaction.

### Additional Notes

* For security reasons, the Firebase service account key is stored in the `.gitignore` file and should not be committed to the repository.
* This is a basic example. You can customize the application to fit your specific needs.
