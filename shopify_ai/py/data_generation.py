"""ShopifyAI data generation helpers."""
from dataclasses import dataclass

import datetime
import itertools
import random
import faker

from google.cloud import bigquery


@dataclass
class ProductOptions:
    """Product options used to generate unique products."""
    collections: list[str]
    adjectives: list[str]
    colors: list[str]
    materials: list[str]
    product_types: list[str]
    vendors: list[str]
    statuses: list[str]


@dataclass
class ProductDatum:  # pylint: disable=too-many-instance-attributes
    """Shopify data associated with a single product."""
    title: str
    adjective: str
    color: str
    material: str
    product_type: str
    vendor: str
    status: str
    collection: str


def _generate_product_data(
    product_options: ProductOptions
) -> list[ProductDatum]:
    """Generates a list of unique product details, based on the product_options provided.

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
    adjectives = product_options.adjectives
    collections = product_options.collections
    colors = product_options.colors
    materials = product_options.materials
    product_types = product_options.product_types
    statuses = product_options.statuses
    vendors = product_options.vendors

    return [
        {
            'title': f'{adj} {color} {material} {product_type}',
            'adjective': adj,
            'color': color,
            'material': material,
            'product_type': product_type,
            'vendor': random.choice(vendors),
            'status': random.choice(statuses),
            'collection': random.choice(collections),
        }
        for adj, color, material, product_type in itertools.product(
            adjectives, colors, materials, product_types
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
    product_options: ProductOptions,
    num_products: int = 100,
) -> list[ProductDatum]:
    """Generates dummy data for a Shopify product.

    Args:
      product_options: The product options used to generate the products
      num_products: The number of products to generate

    Yields:
      A list of product data
    """
    unique_product_details = _generate_product_data(
        product_options=product_options
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
    product_options: ProductOptions,
    num_products: int = 100,
) -> str:
    """Creates dummy data and uploads it to BigQuery.

    Args:
      bq_client: The BigQuery client
      project_id: The project ID
      schema: The schema of the table
      product_options: The product options used to generate dummy data
      num_products: The number of products to generate

    Returns:
      A string indicating whether the operation was successful or not
    """
    dummy_data = list(
        generate_dummy_data(
            product_options=product_options,
            num_products=num_products,
        )
    )

    table_id = f'{project_id}.shopify_ai.shopify_products'
    table = bigquery.Table(table_id, schema=schema)

    table = bq_client.create_table(table, exists_ok=True)

    errors = bq_client.insert_rows_json(table, dummy_data)

    if errors:
        return f'Encountered errors: {errors}'
    return 'Successfully inserted rows into BigQuery table.'
