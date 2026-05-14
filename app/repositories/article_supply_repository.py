import logging

from app.repositories.database import connect_db


logger = logging.getLogger(__name__)


def list_all():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT article, supply_name FROM art_supp")
    rows = cur.fetchall()
    con.close()
    logger.debug("Article supplies selected from SQLite: count=%s", len(rows))
    return rows


def add(article, supply_name):
    con = connect_db()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO art_supp (article, supply_name) VALUES (?, ?)",
        (article, supply_name),
    )
    con.commit()
    con.close()
    logger.info("Article supply saved to SQLite: article=%r supply_name=%r", article, supply_name)


def clear():
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM art_supp")
    con.commit()
    con.close()
    logger.info("All article supplies deleted from SQLite")


def replace(rows):
    clear()

    con = connect_db()
    cur = con.cursor()
    cur.executemany("INSERT INTO art_supp VALUES (?, ?)", rows)
    con.commit()
    con.close()
    logger.info("Article supplies replaced in SQLite: rows_count=%s", len(rows))
