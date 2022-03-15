from metatrader import MetaTrader
from utils import (
    read_json,
    accounts_json_filename,
    get_today_date,
    save_to_db,
    delete_data_from_db
)


def calculate_max_loss(data, mtrader):
    symbol = data["symbol"]
    quote_pair = symbol[:3]
    base_pair = symbol[3:6]
    max_loss = None
    bid_price = 1

    if base_pair != "GBP":
        symbol_pair = f"GBP{base_pair}"
        # Get symbol tick info from MT5
        symbol_ticke_info = mtrader.get_symbol_tick_info(symbol_pair)
        if symbol_ticke_info:
            bid_price = symbol_ticke_info["bid"]

    # Max Loss calculation
    if data["type"] == 1:
        max_loss = (data["volume"] * 100000 *
                    (data["price_open"] - data["sl"])) / bid_price
    else:
        max_loss = (data["volume"] * 100000 *
                    (data["sl"] - data["price_open"])) / bid_price

    if quote_pair == "XAG":
        max_loss = max_loss / 20
    elif quote_pair in ["XAU", "XPT", "XPR"]:
        max_loss = max_loss / 1000

    data["max_loss"] = max_loss

    return data


def process_account(account_meta):
    mtrader = MetaTrader(account_meta=account_meta)

    at_risk = None

    today_date = get_today_date()

    # Get Account info
    account_data = mtrader.get_account_info(today_date=today_date)
    if account_data:
        save_to_db([account_data], table_name="account_info")

    # Get Positions info
    positions_data = mtrader.get_positions_info(
        today_date=today_date, account_number=mtrader.account_num)
    if positions_data:
        # calculate max_loss for each position
        positions_data = list(
            map(lambda data: calculate_max_loss(data, mtrader), positions_data))

        at_risk = sum(list(map(lambda data: data["max_loss"] if data["max_loss"] else 0, positions_data)))

        # delete existing data from database table
        delete_data_from_db({"login": mtrader.account_num,
                            "_date": today_date}, table_name="positions_info")

        # save data to table
        save_to_db(positions_data, table_name="positions_info")

    # Get Trade History info
    trade_history_data = mtrader.get_trade_history(
        today_date=today_date, account_number=mtrader.account_num)
    if trade_history_data:
        save_to_db(trade_history_data, table_name="trade_history")

    # Close MT5 connection
    mtrader.close_connection()

    # Account summary data saving
    # delete existing data from database table
    delete_data_from_db({"account_name": mtrader.account_num,
                        "_date": today_date}, table_name="portfolio_account")

    deposits = account_meta["deposits"]
    equity = account_data["equity"]
    portfolio_account_data = {
        "account_name": mtrader.account_num,
        "deposits": deposits,
        "balance": account_data["balance"],
        "profit": equity - deposits,
        "equity": equity,
        "pnl_percentage": ((equity - deposits) / equity) * 100,
        "_date": today_date,
        "margin_free": account_data["margin_free"],
        "at_risk": at_risk,
    }
    save_to_db([portfolio_account_data], table_name="portfolio_account")


def main():
    accounts = read_json(accounts_json_filename)
    list(map(process_account, accounts))


if __name__ == "__main__":
    main()
