import logging

from app.services.article_supply_service import list_article_supplies
from app.services.orders_service import fetch_id, update_tasks
from app.services.supplies_service import (
    clear_supplies,
    create_supply,
    delete_supp,
    patch_supply,
)


logger = logging.getLogger(__name__)


def process_article_supply(article, supply_name):
    logger.info("Processing article supply: article=%r supply_name=%r", article, supply_name)
    order_ids = fetch_id(article)

    if len(order_ids) == 0:
        logger.warning("Skipping article supply because no orders were found: article=%r supply_name=%r", article, supply_name)
        return False

    logger.info(
        "Orders found for article supply: article=%r supply_name=%r orders_count=%s",
        article,
        supply_name,
        len(order_ids),
    )
    try:
        supply_id = create_supply(supply_name)
        patch_supply(supply_id, order_ids)
    except Exception:
        logger.exception("Article supply processing failed: article=%r supply_name=%r", article, supply_name)
        raise

    logger.info(
        "Article supply processed: article=%r supply_name=%r orders_count=%s",
        article,
        supply_name,
        len(order_ids),
    )
    return True


def calculate_run_time():
    count = 0
    article_supplies = list_article_supplies()
    logger.info("Calculating resort run time: article_supplies_count=%s", len(article_supplies))
    for article, _supply_name in article_supplies:
        count += len(fetch_id(article))

    logger.info("Calculated resort run time: orders_count=%s", count)
    return count


def sort_tasks():
    logger.info("Sorting tasks requested with cached supplies reset")
    delete_supp()
    resort_tasks()


def resort_tasks():
    logger.info("Resort tasks started")
    update_tasks()

    article_supplies = list_article_supplies()
    logger.info("Article supplies loaded for resort: count=%s", len(article_supplies))
    processed_count = 0
    skipped_count = 0

    for article, supply_name in article_supplies:
        if process_article_supply(article, supply_name):
            processed_count += 1
        else:
            skipped_count += 1

    logger.info("Resort tasks finished: processed=%s skipped=%s", processed_count, skipped_count)
