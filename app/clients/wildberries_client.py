import logging

from requests import RequestException, request

from app.config.env import get_wb_api_token


MARKETPLACE_API_URL = "https://marketplace-api.wildberries.ru/api/v3"
COMMON_API_URL = "https://common-api.wildberries.ru"
REQUEST_TIMEOUT = 30
MAX_RESPONSE_LOG_LENGTH = 500

logger = logging.getLogger(__name__)


class WildberriesAPIError(Exception):
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class WildberriesAuthError(WildberriesAPIError):
    pass


def authorization():
    return {"Authorization": get_wb_api_token()}


def _request(method, url, allowed_status_codes=None, **kwargs):
    allowed_status_codes = allowed_status_codes or set()
    logger.debug("Wildberries request started: method=%s url=%s", method, url)

    try:
        response = request(
            method,
            url,
            headers=authorization(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except RequestException as e:
        logger.exception("Wildberries request failed: method=%s url=%s", method, url)
        raise WildberriesAPIError(
            f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0441\u043e\u0435\u0434\u0438\u043d\u0435\u043d\u0438\u044f \u0441 Wildberries: {e}"
        ) from e

    logger.info(
        "Wildberries response received: method=%s url=%s status_code=%s",
        method,
        url,
        response.status_code,
    )

    if response.status_code == 401:
        logger.warning("Wildberries authorization failed: method=%s url=%s", method, url)
        raise WildberriesAuthError(
            "\u041d\u0435\u0432\u0435\u0440\u043d\u044b\u0439 \u0438\u043b\u0438 \u043f\u0440\u043e\u0441\u0440\u043e\u0447\u0435\u043d\u043d\u044b\u0439 API \u0442\u043e\u043a\u0435\u043d Wildberries",
            401,
            response.text,
        )

    if response.status_code >= 400 and response.status_code not in allowed_status_codes:
        logger.warning(
            "Wildberries returned error: method=%s url=%s status_code=%s response=%r",
            method,
            url,
            response.status_code,
            response.text[:MAX_RESPONSE_LOG_LENGTH],
        )
        raise WildberriesAPIError(
            f"Wildberries API \u0432\u0435\u0440\u043d\u0443\u043b \u043e\u0448\u0438\u0431\u043a\u0443 {response.status_code}",
            response.status_code,
            response.text,
        )

    return response


def _json(response):
    try:
        return response.json()
    except ValueError as e:
        logger.exception(
            "Wildberries returned invalid JSON: status_code=%s response=%r",
            response.status_code,
            response.text[:MAX_RESPONSE_LOG_LENGTH],
        )
        raise WildberriesAPIError(
            "Wildberries API \u0432\u0435\u0440\u043d\u0443\u043b \u043d\u0435\u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u044b\u0439 JSON",
            response.status_code,
            response.text,
        ) from e


def get_new_orders():
    res = _request("GET", f"{MARKETPLACE_API_URL}/orders/new")
    data = _json(res)
    orders_count = sum(len(orders) for orders in data.values())
    logger.info("Loaded new Wildberries orders: count=%s", orders_count)
    return data


def get_supply(supply_id):
    return _request("GET", f"{MARKETPLACE_API_URL}/supplies/{supply_id}", allowed_status_codes={404})


def create_supply(name):
    res = _request("POST", f"{MARKETPLACE_API_URL}/supplies", json={"name": name})
    data = _json(res)

    try:
        supply_id = data["id"]
        logger.info("Created Wildberries supply: supply_id=%s name=%r", supply_id, name)
        return supply_id
    except KeyError as e:
        logger.exception("Wildberries create supply response has no id: name=%r", name)
        raise WildberriesAPIError(
            "Wildberries API \u043d\u0435 \u0432\u0435\u0440\u043d\u0443\u043b id \u0441\u043e\u0437\u0434\u0430\u043d\u043d\u043e\u0439 \u043f\u043e\u0441\u0442\u0430\u0432\u043a\u0438",
            res.status_code,
            res.text,
        ) from e


def add_order_to_supply(supply_id, order_id):
    url = f"{MARKETPLACE_API_URL}/supplies/{supply_id}/orders/{order_id}"
    response = _request("PATCH", url)
    logger.info("Added order to Wildberries supply: supply_id=%s order_id=%s", supply_id, order_id)
    return response


def ping():
    return _request("GET", f"{COMMON_API_URL}/ping")


def check_connect():
    try:
        is_connected = ping().status_code == 200
        logger.info("Wildberries connection check finished: connected=%s", is_connected)
        return is_connected
    except WildberriesAPIError:
        logger.exception("Wildberries connection check failed")
        return False


def is_token_expired():
    try:
        ping()
        logger.info("Wildberries token check finished: expired=False")
        return False
    except WildberriesAuthError:
        logger.warning("Wildberries token check finished: expired=True")
        return True
