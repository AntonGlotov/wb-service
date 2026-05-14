import logging

from app.repositories.database import connect_db


logger = logging.getLogger(__name__)


def list_supply_ids():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT supplyId FROM supplies")
    supply_ids = [row[0] for row in cur.fetchall()]
    con.close()
    logger.debug("Supply ids selected from SQLite: count=%s", len(supply_ids))
    return supply_ids


def get_id_by_name(name):
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT supplyId FROM supplies WHERE supply_name = ?", (name,))
    result = cur.fetchone()
    con.close()
    logger.debug("Supply id selected by name: name=%r found=%s", name, result is not None)
    return result[0] if result else None


def save(name, supply_id):
    con = connect_db()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO supplies (supply_name, supplyId) VALUES (?, ?)",
        (name, supply_id),
    )
    con.commit()
    con.close()
    logger.info("Supply saved to SQLite: supply_id=%s name=%r", supply_id, name)


def delete_by_id(supply_id):
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM supplies WHERE supplyId = ?", (supply_id,))
    con.commit()
    con.close()
    logger.info("Supply deleted from SQLite: supply_id=%s", supply_id)


def delete_all():
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM supplies")
    con.commit()
    con.close()
    logger.info("All supplies deleted from SQLite")
