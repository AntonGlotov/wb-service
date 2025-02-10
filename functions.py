import requests
from requests import get, patch, post
from dotenv import load_dotenv, find_dotenv, set_key
from os import getenv, environ
from sqlite3 import connect


def authorization():  # Авторизация по Токену
    load_dotenv()
    token = getenv('wb_api_token')

    headers = {
        'Authorization': token
    }
    return headers


def update_env_api(key, value):
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)
    set_key(dotenv_file, key, value)
    load_dotenv(dotenv_file, override=True)


def get_new_orders():  # Получить список новых заказов
    url_get_inf = 'https://suppliers-api.wildberries.ru/api/v3/orders/new'
    res = get(url_get_inf, headers=authorization())
    return res.json()


def delete_tasks():  # Очистить таблицу tasks
    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute('DELETE FROM `tasks`')
    con.commit()


def update_tasks():  # Добавить в бд все новые заказы

    delete_tasks()  # Очищение tasks

    new_orders = get_new_orders()
    con = connect('database.sqlite3')
    cur = con.cursor()
    for keys, values in new_orders.items():
        for i in values:
            # Проверка на повторное добавление
            cur.execute('SELECT id from tasks')
            all_ids = [row[0] for row in cur.fetchall()]
            if i["id"] not in all_ids:
                cur.execute(
                    'INSERT INTO tasks (id, article) VALUES (?,?)',
                    (
                        i["id"], i["article"]))
    con.commit()
    con.close()


def clear_supplies():
    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute('SELECT supplyId FROM supplies')
    for x in cur.fetchall():
        temp = (get(f'https://marketplace-api.wildberries.ru/api/v3/supplies/{x[0]}', headers=authorization()))
        if temp.status_code == 200 and temp.json()['done']:
            cur.execute('DELETE FROM `supplies` WHERE supplyId = ?', (x[0],))

    con.commit()
    con.close()


def create_supply(name):  # Изменение таблицы соответствий. На входе имя поставки. На выходе wb-gi

    con = connect('database.sqlite3')
    cur = con.cursor()

    cur.execute('SELECT supply_name, supplyid FROM supplies WHERE supply_name = ?', (name,))
    result = cur.fetchall()

    if len(result) != 0:  # Если запись уже существует, возвращаем существующий supplyId
        return result[0][1]

    else:  # Если запись не существует, создаем новую
        url_post = 'https://suppliers-api.wildberries.ru/api/v3/supplies'
        name_supp = {
            'name': name
        }
        res = post(url_post, headers=authorization(), json=name_supp)
        wb_gi = res.json()['id']

        cur.execute(
            'INSERT INTO supplies (supply_name, supplyId) VALUES (?,?)', (name, wb_gi)
        )
        con.commit()

    con.close()
    return wb_gi


def delete_supp():
    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute('DELETE FROM `supplies`')
    con.commit()


def fetch_id(articles):  # Возвращает id всех заказов с передаваемым артикулом
    con = connect('database.sqlite3')
    cur = con.cursor()
    ids = []
    if isinstance(articles, list):  # Если передан массив
        for i in articles:
            cur.execute("SELECT id FROM tasks WHERE article = ?", (i,))
            ids1 = cur.fetchall()
            for j in ids1:
                ids.append(j[0])

    else:  # Если передана строка
        cur.execute("SELECT id FROM tasks WHERE article = ?", (articles,))
        ids1 = cur.fetchall()
        for j in ids1:
            ids.append(j[0])

    con.commit()
    con.close()
    return ids


def patch_supply(supplyid, orders):  # Добавить сборочные задания к поставке

    headers = authorization()

    if isinstance(orders, list):  # Если передан массив
        for i in range(len(orders)):
            url = f'https://marketplace-api.wildberries.ru/api/v3/supplies/{supplyid}/orders/{orders[i]}'
            patch(url, headers=headers)


    else:  # Если передана строка
        url = f'https://marketplace-api.wildberries.ru/api/v3/supplies/{supplyid}/orders/{orders}'
        patch(url, headers=headers)


def update_art_supp(art, suuply_name):
    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute(
        'INSERT INTO art_supp (article, supply_name) VALUES (?,?)', (art, suuply_name)
    )

    con.commit()
    con.close()


def calculate_run_time():
    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute('SELECT article, supply_name FROM art_supp')
    temp = cur.fetchall()

    count = 0
    for x in temp:
        tasks_id = fetch_id(x[0])
        count += len(tasks_id)
    return count


def sort_tasks():
    delete_supp()
    update_tasks()

    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute('SELECT article, supply_name FROM art_supp')

    for x in cur.fetchall():
        a = fetch_id(x[0])

        if len(a) == 0:
            continue

        patch_supply(create_supply(x[1]), a)
    con.commit()
    con.close()


def resort_tasks():
    update_tasks()

    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute('SELECT article, supply_name FROM art_supp')

    for x in cur.fetchall():
        a = fetch_id(x[0])

        if len(a) == 0:
            continue

        patch_supply(create_supply(x[1]), a)
    con.commit()
    con.close()


# if __name__ == '__main__':
    # sort_tasks()
    # update_tasks()

    # update_env_api('papa', '123123')


    # clear_supplies()