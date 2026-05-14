import logging

from app.repositories import article_supply_repository


logger = logging.getLogger(__name__)


def update_art_supp(article, supply_name):
    article_supply_repository.add(article, supply_name)
    logger.info("Article supply updated: article=%r supply_name=%r", article, supply_name)


def list_article_supplies():
    rows = article_supply_repository.list_all()
    logger.debug("Article supplies listed: count=%s", len(rows))
    return rows
