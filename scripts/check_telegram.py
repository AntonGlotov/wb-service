from app.config.env import get_telegram_token


def main():
    token = get_telegram_token()
    url = f"https://api.telegram.org/bot{token}/getMe"

    print("Checking Telegram Bot API with requests...")
    import requests

    response = requests.get(url, timeout=30)
    print(response.status_code, response.json().get("ok"))

    print("Checking Telegram Bot API with httpx...")
    import httpx

    response = httpx.get(url, timeout=30)
    print(response.status_code, response.json().get("ok"))


if __name__ == "__main__":
    main()
