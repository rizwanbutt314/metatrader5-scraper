import json
import os
import mysql.connector
from datetime import date

basepath = os.path.dirname(os.path.abspath(__file__))
accounts_json_filename = "accounts.json"

# MYSQL Settings
DB_HOST = "localhost"
DB_USERNAME = "root"
DB_PASSWORD = "!frt_"
DB_DATABASE = "frx"

TABLES_MAPPING = {
    "account_info": {
        "where_columns": ["login", "_date"],
        "columns": [
            "login",
            "trade_mode",
            "leverage",
            "limit_orders",
            "margin_so_mode",
            "trade_allowed",
            "trade_expert",
            "margin_mode",
            "currency_digits",
            "fifo_close",
            "balance",
            "credit",
            "profit",
            "equity",
            "margin",
            "margin_free",
            "margin_level",
            "margin_so_call",
            "margin_so_so",
            "margin_initial",
            "margin_maintenance",
            "assets",
            "liabilities",
            "commission_blocked",
            "name",
            "server",
            "currency",
            "company",
            "_date",
        ]
    },
    "positions_info": {
        "where_columns": ["login", "_date"],
        "columns": [
            "ticket",
            "time",
            "type",
            "magic",
            "identifier",
            "reason",
            "volume",
            "price_open",
            "sl",
            "tp",
            "price_current",
            "swap",
            "profit",
            "symbol",
            "comment",
            "login",
            "_date",
            "max_loss",
        ]
    },
    "trade_history": {
        "where_columns": ["ticket", "login", "_date"],
        "columns": [
            "ticket",
            "time_setup",
            "time_setup_msc",
            "time_done",
            "time_done_msc",
            "type",
            "type_filling",
            "magic",
            "position_id",
            "volume_initial",
            "price_open",
            "price_current",
            "symbol",
            "comment",
            "external_id",
            "login",
            "_date",
        ]
    },
    "portfolio_account": {
        "where_columns": ["account_name", "_date"],
        "columns": [
            "account_name",
            "deposits",
            "balance",
            "profit",
            "equity",
            "pnl_percentage",
            "_date",
            "at_risk",
            "margin_free"
        ]
    },
}


def get_today_date():
    today = date.today()
    return today.strftime("%Y-%m-%d")


def read_json(filename):
    data = list()
    filepath = os.path.join(basepath, filename)
    with open(filepath, "r") as f:
        data = json.load(f)

    return data


def delete_data_from_db(data, table_name=""):
    if not table_name:
        raise Exception("Table Name missing...")

    table_meta_data = TABLES_MAPPING[table_name]
    where_columns = table_meta_data["where_columns"]
    where_columns_cols_str = " AND ".join(
        [f"{col} = %s" for col in where_columns])

    where_columns_vals = (data.get(col, None) for col in where_columns)

    mydb = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor(buffered=True)

    sql = f"""DELETE FROM {table_name} WHERE {where_columns_cols_str}"""
    val = (*where_columns_vals, )
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
    mydb.close()


def save_to_db(data, table_name=""):
    if not table_name:
        raise Exception("Table Name missing...")

    table_meta_data = TABLES_MAPPING[table_name]
    where_columns = table_meta_data["where_columns"]
    columns = table_meta_data["columns"]

    update_query_cols_str = ", ".join([f"{col} = %s" for col in columns])

    insert_query_cols_str = ", ".join([f"{col}" for col in columns])
    insert_query_vals_str = ", ".join([f"%s" for col in columns])

    where_columns_cols_str = " AND ".join(
        [f"{col} = %s" for col in where_columns])

    mydb = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        auth_plugin='mysql_native_password'
    )

    mycursor = mydb.cursor(buffered=True)

    # Check for duplicates
    filtered_data = list()
    for record in data:

        where_columns_vals = (record.get(col, None) for col in where_columns)

        # Check existing entry
        sql = f"""SELECT * FROM {table_name} WHERE {where_columns_cols_str}"""
        val = (*where_columns_vals, )

        mycursor.execute(sql, val)
        myresult = mycursor.fetchone()

        if not myresult:
            filtered_data.append(record)
        else:
            # Update the existing data
            update_query_cols = (record.get(col, None) for col in columns)
            where_columns_vals = (record.get(col, None)
                                  for col in where_columns)

            sql = f"""UPDATE {table_name} SET {update_query_cols_str} WHERE {where_columns_cols_str} """
            val = (*update_query_cols, *where_columns_vals)
            mycursor.execute(sql, val)
            mydb.commit()

    # INSERT data
    sql = f"INSERT INTO {table_name} ({insert_query_cols_str}) VALUES ({insert_query_vals_str})"

    data_to_db = [tuple((fd.get(col, None) for col in columns))
                  for fd in filtered_data]
    mycursor.executemany(sql, data_to_db)
    mydb.commit()

    mycursor.close()
    mydb.close()
