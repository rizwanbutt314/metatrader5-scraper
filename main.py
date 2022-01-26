from metatrader import MetaTrader
from utils import (
    read_json,
    accounts_json_filename,
    get_today_date,
    save_to_db,
    delete_data_from_db
)


def process_account(account_meta):
    mtrader = MetaTrader(account_meta=account_meta)

    today_date = get_today_date()

    # Get Account info
    account_data = mtrader.get_account_info(today_date=today_date)
    if account_data:
        save_to_db([account_data], table_name="account_info")

    # Get Positions info
    positions_data = mtrader.get_positions_info(
        today_date=today_date, account_number=mtrader.account_num)
    if positions_data:
        delete_data_from_db({"login": mtrader.account_num,
                            "_date": today_date}, table_name="positions_info")
        save_to_db(positions_data, table_name="positions_info")

    # Get Trade History info
    trade_history_data = mtrader.get_trade_history(
        today_date=today_date, account_number=mtrader.account_num)
    if trade_history_data:
        save_to_db(trade_history_data, table_name="trade_history")

    # Close MT5 connection
    mtrader.close_connection()


def main():
    accounts = read_json(accounts_json_filename)
    list(map(process_account, accounts))


if __name__ == "__main__":
    main()
