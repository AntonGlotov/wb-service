from os import getenv
from dotenv import load_dotenv
import requests
from sqlite3 import connect
from datetime import datetime


def authorization():  # Авторизация по Токену
    load_dotenv()
    token = getenv('wb_api_token')

    headers = {
        'Authorization': token
    }
    return headers


def update_db():
    param = {
        'limit': 500,
        'next': 0
    }
    res = requests.get('https://marketplace-api.wildberries.ru/api/v3/supplies', headers=authorization(), params=param)

    con = connect('databasereport.sqlite3')
    cur = con.cursor()

    cur.execute('DELETE FROM `supplies`')

    for x in res.json()['supplies']:
        cur.execute(
            'INSERT INTO supplies VALUES (?, ?, ?, ?, ?, ?, ?)',
            (x['id'], x['name'], x['createdAt'], x['closedAt'], x['scanDt'], x['rejectDt'], x['done'])
        )

    con.commit()
    con.close()


def count_tasks(supplyId):
    res = requests.get(f'https://marketplace-api.wildberries.ru/api/v3/supplies/{supplyId}/orders',
                       headers=authorization())
    return len(res.json()['orders'])


def make_report(start_end_dates):
    if len(start_end_dates) == 1:
        dt = datetime.strptime(start_end_dates[0], "%d.%m.%Y")
        formatted_date = dt.strftime("%Y-%m-%d")
        con = connect('databasereport.sqlite3')
        cur = con.cursor()
        cur.execute('SELECT id, name FROM supplies WHERE date(scanDt) = ?', (formatted_date,))

    else:
        dt_start = datetime.strptime(start_end_dates[0], "%d.%m.%Y")
        dt_end = datetime.strptime(start_end_dates[1], "%d.%m.%Y")
        formatted_date_start = dt_start.strftime("%Y-%m-%d")
        formatted_date_end = dt_end.strftime("%Y-%m-%d")
        con = connect('databasereport.sqlite3')
        cur = con.cursor()
        cur.execute('SELECT id, name FROM supplies WHERE date(scanDt) >= ? AND date(scanDt) <= ?', (formatted_date_start, formatted_date_end))


    response = {}
    fetched = cur.fetchall()
    con.commit()
    con.close()
    if not fetched:
        return 'В этот день поставок не обнаружено'

    for x in fetched:
        response[x[1]] = count_tasks(x[0])
    result_lines = ['Отгружены']
    for key, value in response.items():
        result_lines.append(f"{key} --- {value} шт")
    result_lines.append('_________________')
    result_lines.append(f'Всего: {str(sum(response.values()))}')

    return "\n".join(result_lines)


def dict_to_string(data_dict):
    result_lines = []

    for key, value in data_dict.items():
        result_lines.append(f"{key} - {value}")

    return "\n".join(result_lines)


if __name__ == '__main__':
    update_db()

    # print(make_report('26.08.2025', '28.08.2025'))
