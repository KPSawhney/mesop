## Shopify AI with Mesop

This document details a web application built with Mesop that leverages Gemini to analyze Shopify data stored in BigQuery. Users can sign in with their Google accounts and ask questions about their store's products. 

### Project Structure

* **py:** Core application logic
    * `main.py`: Defines the main page and handles user interactions.
    * `shopify_ai.py`: Handles data transformation and interacts with Gemini.
* **secrets:** Stores GCP credentials (`.gitignore`d for security).
* **app.yaml:** Configuration for deploying the app to Google App Engine.
* **requirements.txt:** Lists project dependencies.
* **README.md:** This file.

### Prerequisites

* Python 3.6+
* Google Cloud SDK
* GCP project ID
* Gemini API Key

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set environment variables:**
   * Replace the placeholder values in `app.yaml` with your Firebase project's configuration (if deploying to Google App Engine).
   * Set the following environment variables:
      * `GCP_PROJECT_ID`: Your Google Cloud project ID.
      * `GEMINI_API_KEY`: Your API key for the generative AI model (Bard).

### Generating Sample Data (Optional)

This project demonstrates querying BigQuery data. To follow along, you'll need sample data in BigQuery. You can use the included functions in `shopify_ai.py` to generate dummy data for the `shopify_products` table.

### Deployment (Optional)

Configure `app.yaml` with your project details and deploy the app to Google App Engine using the Google Cloud SDK.

### How it Works

1. Upon receiving a user query about Shopify products, the `shopify_ai.py` script transforms the question and interacts with the generative AI model.
2. The generative AI model analyzes the schema of the `shopify_products` table in BigQuery and writes an SQL script to answer the user's question.
3. The script is executed in BigQuery, and the results are passed back to the LLM to answer the question for the user.
