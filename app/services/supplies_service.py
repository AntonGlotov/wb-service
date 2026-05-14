import logging

from app.clients import wildberries_client
from app.repositories import supplies_repository


logger = logging.getLogger(__name__)


def clear_supplies():
    supply_ids = supplies_repository.list_supply_ids()
    logger.info("Clearing inactive supplies: count=%s", len(supply_ids))

    deleted_count = 0
    kept_count = 0
    for supply_id in supply_ids:
        response = wildberries_client.get_supply(supply_id)
        if response.status_code == 404:
            logger.info("Deleting cached supply missing in Wildberries: supply_id=%s", supply_id)
            supplies_repository.delete_by_id(supply_id)
            deleted_count += 1
        elif response.status_code == 200 and response.json()["done"]:
            logger.info("Deleting completed cached supply: supply_id=%s", supply_id)
            supplies_repository.delete_by_id(supply_id)
            deleted_count += 1
        else:
            logger.debug("Keeping active cached supply: supply_id=%s status_code=%s", supply_id, response.status_code)
            kept_count += 1

    logger.info("Inactive supplies clearing finished: deleted=%s kept=%s", deleted_count, kept_count)


def create_supply(name):
    supply_id = supplies_repository.get_id_by_name(name)
    if supply_id is not None:
        logger.info("Using cached supply: supply_id=%s name=%r", supply_id, name)
        return supply_id

    supply_id = wildberries_client.create_supply(name)
    supplies_repository.save(name, supply_id)
    logger.info("New supply saved locally: supply_id=%s name=%r", supply_id, name)
    return supply_id


def delete_supp():
    logger.info("Deleting all cached supplies")
    supplies_repository.delete_all()


def patch_supply(supply_id, orders):
    order_ids = orders if isinstance(orders, list) else [orders]
    logger.info("Adding orders to supply: supply_id=%s orders_count=%s", supply_id, len(order_ids))

    added_count = 0
    if isinstance(orders, list):
        for order_id in orders:
            try:
                wildberries_client.add_order_to_supply(supply_id, order_id)
                added_count += 1
            except Exception:
                logger.exception("Failed to add order to supply: supply_id=%s order_id=%s", supply_id, order_id)
                raise
    else:
        try:
            wildberries_client.add_order_to_supply(supply_id, orders)
            added_count += 1
        except Exception:
            logger.exception("Failed to add order to supply: supply_id=%s order_id=%s", supply_id, orders)
            raise

    logger.info("Orders added to supply: supply_id=%s added_count=%s", supply_id, added_count)
