import logging

from app.clients import wildberries_client
from app.repositories import tasks_repository


logger = logging.getLogger(__name__)


def update_tasks():
    logger.info("Updating tasks from Wildberries orders")
    new_orders = wildberries_client.get_new_orders()
    orders_count = sum(len(orders) for orders in new_orders.values())
    logger.info("Wildberries orders loaded for tasks update: count=%s", orders_count)
    tasks_repository.replace_from_orders(new_orders)
    logger.info("Tasks update finished: count=%s", orders_count)


def fetch_id(articles):
    if isinstance(articles, list):
        ids = tasks_repository.find_ids_by_articles(articles)
        logger.debug("Fetched order ids by articles: articles_count=%s ids_count=%s", len(articles), len(ids))
        if not ids:
            logger.warning("No order ids found by articles: articles=%r", articles)
        return ids

    ids = tasks_repository.find_ids_by_article(articles)
    logger.debug("Fetched order ids by article: article=%r ids_count=%s", articles, len(ids))
    if not ids:
        logger.warning("No order ids found by article: article=%r", articles)
    return ids
