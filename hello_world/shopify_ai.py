"""ShopifyAI helpers."""

import datetime
import itertools
import random
import faker
from google import generativeai as genai
from google.cloud import bigquery
import sqlparse


def _generate_unique_product_details(
    collections: list[str],
    adjectives: list[str],
    colors: list[str],
    materials: list[str],
    product_type: list[str],
    vendors: list[str],
    status: list[str],
) -> list[dict[str, str]]:
    """Generates a list of unique product details.

    Args:
      collections: A list of clothing collections
      adjectives: A list of adjectives
      colors: A list of colors
      materials: A list of materials
      product_type: A list of product types
      vendors: A list of vendors
      status: A list of product statuses

    Returns:
      A list of unique product details
    """
    return [
        {
            'title': f'{adj} {color} {material} {product_type}',
            'adjective': adj,
            'color': color,
            'material': material,
            'product_type': product_type,
            'vendor': random.choice(vendors),
            'status': status,
            'collection': random.choice(collections),
        }
        for adj, color, material, product_type in itertools.product(
            adjectives, colors, materials, product_type
        )
    ]


def _create_product_datum(
    title: str,
    product_type: str,
    status: str,
    collection: str,
) -> dict[str, str]:
    """Creates a product datum.

    Args:
      title: The title of the product
      product_type: The product type
      status: The status of the product
      collection: The collection of the product

    Returns:
      A product datum
    """
    fake = faker.Faker()

    total_quantity_sold = random.randint(1, 100)
    price = random.randint(5, 100)
    total_quantity_returned = round(
        total_quantity_sold * random.randint(1, 2) / 10, 0
    )

    total_sold = round(total_quantity_sold * price, 2)
    total_discount = round(total_sold * random.randint(1, 2) / 10, 0)

    subtotal_sold = total_sold - total_discount

    created_ts = fake.date_time_between_dates(
        datetime_start=datetime.date(datetime.date.today().year, 1, 1),
        datetime_end=datetime.datetime.now() - datetime.timedelta(days=7),
    ).isoformat()

    net_refunds = round(subtotal_sold / random.randint(1, 10), 0)
    total_discount = round(total_quantity_sold * random.randint(1, 2) / 10, 0)

    return {
        'product_id': fake.random_int(min=1, max=1000000),
        'product_type': product_type,
        'title': title,
        'status': status,
        'created_timestamp': created_ts,
        'collections': collection,
        'count_variants': fake.random_int(min=1, max=10),
        'has_product_image': fake.boolean(),
        'total_quantity_sold': total_quantity_sold,
        'subtotal_sold': subtotal_sold,
        'quantity_sold_net_refunds': (
            total_quantity_sold - total_quantity_returned
        ),
        'subtotal_sold_net_refunds': subtotal_sold - (
            total_quantity_returned * price
        ),
        'product_total_discount': total_discount,
        'product_total_tax': (subtotal_sold - net_refunds) * 0.2,
    }


def generate_dummy_data(
    collections: list[str],
    adjectives: list[str],
    colors: list[str],
    materials: list[str],
    product_type: list[str],
    vendors: list[str],
    status: list[str],
    num_products: int = 100,
) -> list[dict[str, str]]:
    """Generates dummy data for a Shopify product.

    Args:
      collections: A list of clothing collections
      adjectives: A list of adjectives
      colors: A list of colors
      materials: A list of materials
      product_type: A list of product types
      vendors: A list of vendors
      status: A list of product statuses
      num_products: The number of products to generate

    Yields:
      A list of product data
    """
    unique_product_details = _generate_unique_product_details(
        collections=collections,
        adjectives=adjectives,
        colors=colors,
        materials=materials,
        product_type=product_type,
        vendors=vendors,
        status=status,
    )

    num_unique_products = len(unique_product_details)
    if num_products > num_unique_products:
        num_products = num_unique_products
        print(
            'Number of products capped at the number of unique products'
            f' ({num_unique_products})'
        )
    i = 0

    while i <= num_products:
        for i, product_dict in enumerate(unique_product_details):
            yield _create_product_datum(**product_dict)
            i += 1


def create_data_and_upload_to_bigquery(
    bq_client: bigquery.Client,
    project_id: str,
    schema: str,
    collections: list[str],
    adjectives: list[str],
    colors: list[str],
    materials: list[str],
    product_type: list[str],
    vendors: list[str],
    status: list[str],
    num_products: int = 100,
) -> str:
    """Creates dummy data and uploads it to BigQuery.

    Args:
      bq_client: The BigQuery client
      project_id: The project ID
      schema: The schema of the table
      collections: A list of clothing collections
      adjectives: A list of adjectives
      colors: A list of colors
      materials: A list of materials
      product_type: A list of product types
      vendors: A list of vendors
      status: A list of product statuses
      num_products: The number of products to generate

    Returns:
      A string indicating whether the operation was successful or not
    """
    dummy_data = list(
        generate_dummy_data(
            collections=collections,
            adjectives=adjectives,
            colors=colors,
            materials=materials,
            product_type=product_type,
            num_products=num_products,
            vendors=vendors,
            status=status,
        )
    )

    table_id = f'{project_id}.shopify_ai.shopify_products'
    table = bigquery.Table(table_id, schema=schema)

    table = bq_client.create_table(table, exists_ok=True)

    errors = bq_client.insert_rows_json(table, dummy_data)

    if errors:
        return f'Encountered errors: {errors}'
    else:
        return 'Successfully inserted rows into BigQuery table.'


def ask_gemini_to_write_sql_script(
    question: str,
    schema: str,
    project_id: str,
    model_name: str = 'gemini-1.5-pro',
) -> str:
    """Asks Gemini to write a SQL script to answer a question about Shopify data.

    Args:
      question: The question to ask
      schema: The schema of the table
      project_id: The project ID
      model_name: The name of the model to use

    Returns:
      The SQL script generated by Gemini
    """
    model = genai.GenerativeModel(model_name)
    prompt = f"""You are an expert in analyzing Shopify data.

    The schema of the table is: {schema}

    The name of the table is: `{project_id}.shopify_ai.shopify_products`, and we are using BigQuery.

    Please provide a SQL script that you can use to answer the question posed by the user.

    I will then run that script for you, and provide you with the response so you
    can answer the question.
                                      
    Question: {question}"""
    return model.generate_content(prompt).text


def ask_gemini_about_products(
    question: str,
    schema: str,
    bq_client: bigquery.Client,
    project_id: str,
    model_name: str = 'gemini-1.5-pro',
    max_retries: int = 5,
) -> str:
    """Asks Gemini to answer a question about Shopify data.

    This function will first ask Gemini to write a SQL script to answer the
    question. If the script is successful, the results of the script will be
    used to answer the question. If the script is not successful, the function
    will retry up to `max_retries` times. If the script is still not successful
    after `max_retries` times, the function will return an error message.

    Args:
      question: The question to ask
      schema: The schema of the table
      bq_client: The BigQuery client
      project_id: The project ID
      model_name: The name of the model to use
      max_retries: The maximum number of retries

    Returns:
      The answer to the question
    """
    model = genai.GenerativeModel(model_name)

    retries = 0
    while retries < 3:
        try:
            sql_script = ask_gemini_to_write_sql_script(
                question, schema, project_id)
            sql_script = sql_script.replace('```sql', '').replace('```', '')

            query_job = bq_client.query(sql_script)
            results = query_job.result()
            df = results.to_dataframe()
            sql_results = df.to_markdown()
            sql_script = sqlparse.format(
                sql_script, reindent=True, keyword_case='upper'
            )

            prompt = f"""You are an expert in analyzing Shopify data, and your response is being rendered in a chatbot.

Please answer the question posed by the user, based solely on the results from this SQL query:

{sql_script}

Please include the SQL script that was used, after your answer.

Make sure you format your response so that it renders nicely in markdown.

Results:

{sql_results}

Question: {question}"""

            return model.generate_content(prompt).text
        except Exception:
            if retries >= max_retries:
                return (
                    "Sorry, I couldn't write a SQL script to answer your question -"
                    ' please try rephrasing!'
                )
            print(f'Retrying, attempt {retries} of {max_retries}')
            retries += 1
            continue
