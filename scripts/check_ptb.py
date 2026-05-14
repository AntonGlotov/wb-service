import asyncio

from telegram import Bot
from telegram.request import HTTPXRequest

from app.config.env import get_telegram_proxy_url, get_telegram_token


REQUEST_TIMEOUT = 30


async def main():
    request_kwargs = {
        "connect_timeout": REQUEST_TIMEOUT,
        "read_timeout": REQUEST_TIMEOUT,
        "write_timeout": REQUEST_TIMEOUT,
        "pool_timeout": REQUEST_TIMEOUT,
    }
    proxy_url = get_telegram_proxy_url()
    if proxy_url:
        request_kwargs["proxy_url"] = proxy_url

    bot = Bot(
        token=get_telegram_token(),
        request=HTTPXRequest(**request_kwargs),
    )
    me = await bot.get_me()
    print(me.username)


if __name__ == "__main__":
    asyncio.run(main())
