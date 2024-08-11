"""Main file for ShopifyAI Mesop app."""
import os
from google.cloud import bigquery
import mesop as me
import mesop.labs as mel
from py import gemini_integration

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

print('Project ID is: ', GCP_PROJECT_ID)
# Check if running on App Engine
if os.getenv("GAE_ENV", "").startswith("standard"):
    BQ_CLIENT = bigquery.Client(project=GCP_PROJECT_ID)
    print("Running on Google App Engine, using default credentials.")
else:
    from google.oauth2 import service_account

    KEY_PATH = "secrets/serviceAccountKey.json"
    GCP_CREDS = service_account.Credentials.from_service_account_file(
        KEY_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    BQ_CLIENT = bigquery.Client(
        project=GCP_PROJECT_ID,
        credentials=GCP_CREDS
    )
    print("Running locally, using service account credentials.")


def transform(q: str, history: list[mel.ChatMessage]):
    """Takes user's input & chat history to ShopifyAI function."""
    products_schema = [
        bigquery.SchemaField("product_id", "INT64"),
        bigquery.SchemaField("product_type", "STRING"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("created_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("collections", "STRING"),
        bigquery.SchemaField("count_variants", "INT64"),
        bigquery.SchemaField("has_product_image", "BOOL"),
        bigquery.SchemaField("total_quantity_sold", "FLOAT64"),
        bigquery.SchemaField("subtotal_sold", "FLOAT64"),
        bigquery.SchemaField("quantity_sold_net_refunds", "FLOAT64"),
        bigquery.SchemaField("subtotal_sold_net_refunds", "FLOAT64"),
        bigquery.SchemaField("product_total_discount", "FLOAT64"),
        bigquery.SchemaField("product_total_tax", "FLOAT64"),
    ]

    # Create the prompt based on chat history and new question
    prompt = f"""Prior chat history: {str(history)}

  New question: {q}
  """

    # Create the QueryParams object to pass to the ShopifyAI function
    query_params = gemini_integration.QueryParams(
        question=prompt,
        schema=str(products_schema),
        project_id=GCP_PROJECT_ID,
        max_retries=5  # Set the number of retries as needed
    )

    # Call the ask_gemini_about_products function and return the result
    return gemini_integration.ask_gemini_about_products(
        bq_client=BQ_CLIENT,
        query_params=query_params
    )


@me.page(
    path="/shopify_ai",
    title="ShopifyAI",
)
def page():
    """Mesop chat interface."""
    mel.chat(transform, title="ShopifyAI", bot_user="Gemini")
