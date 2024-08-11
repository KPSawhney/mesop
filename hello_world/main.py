"""Main file for ShopifyAI Mesop app."""

import os
from google import generativeai as genai
from google.cloud import bigquery
import mesop as me
import mesop.labs as mel
import shopify_ai

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_CLIENT = bigquery.Client(project=GCP_PROJECT_ID)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def transform(input: str, history: list[mel.ChatMessage]):
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

  prompt = f"""Prior chat history: {str(history)}

  New question: {input}
  """

  return shopify_ai.ask_gemini_about_products(
      question=prompt, schema=products_schema, bq_client=BQ_CLIENT
  )


@me.page(
    path="/shopify_ai",
    title="ShopifyAI",
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
  mel.chat(transform, title="ShopifyAI", bot_user="Gemini")
