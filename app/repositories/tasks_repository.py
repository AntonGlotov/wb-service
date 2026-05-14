import logging

from app.repositories.database import connect_db


logger = logging.getLogger(__name__)


def delete_all():
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM tasks")
    con.commit()
    con.close()
    logger.info("All tasks deleted from SQLite")


def replace_from_orders(new_orders):
    delete_all()

    con = connect_db()
    cur = con.cursor()
    orders_count = 0
    for values in new_orders.values():
        for order in values:
            cur.execute(
                "INSERT OR IGNORE INTO tasks (id, article) VALUES (?, ?)",
                (order["id"], order["article"]),
            )
            orders_count += 1

    con.commit()
    con.close()
    logger.info("Tasks replaced from orders: orders_count=%s", orders_count)


def find_ids_by_article(article):
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT id FROM tasks WHERE article = ?", (article,))
    ids = [row[0] for row in cur.fetchall()]
    con.close()
    logger.debug("Task ids selected by article: article=%r ids_count=%s", article, len(ids))
    return ids


def find_ids_by_articles(articles):
    ids = []
    for article in articles:
        ids.extend(find_ids_by_article(article))
    logger.debug("Task ids selected by articles: articles_count=%s ids_count=%s", len(articles), len(ids))
    return ids
