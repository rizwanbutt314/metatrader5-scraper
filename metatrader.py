import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime


class MetaTrader:

    def __init__(self, account_meta={}):
        print("MetaTrader5 package author: ", mt5.__author__)
        print("MetaTrader5 package version: ", mt5.__version__)

        if not account_meta:
            raise Exception("Account credentials missing...")

        self.account_num = account_meta.get("account_number", "")
        self.account_password = account_meta.get("password", "")
        self.account_server = account_meta.get("server", "")
        self.account_email = account_meta.get("email", "")

        if not mt5.initialize(login=self.account_num, server=self.account_server, password=self.account_password):
            print(f"initialize() failed, error code = {mt5.last_error()}")
            quit()

    def get_account_info(self, today_date=None):
        """
        {
        'login': 62005889, 'trade_mode': 0, 'leverage': 30, 'limit_orders': 500, 'margin_so_mode': 0, 'trade_allowed': True,
        'trade_expert': True, 'margin_mode': 2, 'currency_digits': 2, 'fifo_close': False, 'balance': 74999.56, 'credit': 0.0,
        'profit': 79.96, 'equity': 75079.52, 'margin': 1215.94, 'margin_free': 73863.58, 'margin_level': 6174.6072997022875,
        'margin_so_call': 90.0, 'margin_so_so': 50.0, 'margin_initial': 0.0, 'margin_maintenance': 0.0, 'assets': 0.0, 'liabilities': 0.0,
        'commission_blocked': 0.0, 'name': 'Oluwatoyan Oluwajimi Oremule', 'server': 'PepperstoneUK-Demo', 'currency': 'GBP',
        'company': 'Pepperstone Limited'
        }

        """
        # connect to the trade account specifying a password and a server
        authorized = mt5.login(
            self.account_num, self.account_password, self.account_server)
        if authorized:
            account_info = mt5.account_info()
            if account_info != None:
                account_info_dict = mt5.account_info()._asdict()
                account_info_dict["_date"] = today_date
                return account_info_dict
        else:
            print(
                f"Failed to connect to trade account 62 with password=mZl, error code = {mt5.last_error()}")

    def get_positions_info(self, today_date=None, account_number=None):
        """
        [
            {
                'ticket': 3277316, 'time': Timestamp('2022-01-25 23:40:30'), 'type': 0, 'magic': 0, 'identifier': 3277316, 'reason': 0, 
                'volume': 0.7, 'price_open': 0.91834, 'sl': 0.90986, 'tp': 0.92388, 'price_current': 0.92037, 'swap': 0.02, 'profit': 14.21, 
                'symbol': 'USDCHF_SB', 'comment': '_SB symbol '
            }
        ]
        """
        positions = mt5.positions_get()
        if positions == None:
            print(f"No positions, error code = {mt5.last_error()}")
        elif len(positions) > 0:
            print(f"Total positions = {len(positions)}")
            df = pd.DataFrame(
                list(positions), columns=positions[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.drop(['time_update', 'time_msc', 'time_update_msc',
                     'external_id'], axis=1, inplace=True)
            df['_date'] = today_date
            df['login'] = account_number
            df = df.astype({"time": str})
            return df.to_dict("records")

    def get_trade_history(self, today_date=None, account_number=None):
        """
        [
            {
                'ticket': 3277316, 'time_setup': Timestamp('2022-01-25 23:40:30'), 'time_setup_msc': 1643154030662, 
                'time_done': Timestamp('2022-01-25 23:40:30'), 'time_done_msc': 1643154030662, 'type': 0, 'type_filling': 1, 
                'magic': 0, 'position_id': 3277316, 'volume_initial': 0.7, 'price_open': 0.0, 'price_current': 0.91834, 
                'symbol': 'USDCHF_SB', 'comment': '_SB symbol ', 'external_id': ''
            }
        ]
        """
        from_date = datetime(2020, 1, 1)
        to_date = datetime.now()

        history_orders = mt5.history_orders_get(from_date, to_date)
        if history_orders == None:
            print("No history orders, error code={}".format(mt5.last_error()))
        elif len(history_orders) > 0:
            print("history_orders_get({}, {}, )={}".format(
                from_date, to_date, len(history_orders)))

            df = pd.DataFrame(list(history_orders),
                              columns=history_orders[0]._asdict().keys())
            df.drop(
                ['time_expiration', 'type_time', 'state', 'position_by_id', 'reason', 'volume_current', 'price_stoplimit',
                 'sl',
                 'tp'], axis=1, inplace=True)
            df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
            df['time_done'] = pd.to_datetime(df['time_done'], unit='s')
            df['_date'] = today_date
            df['login'] = account_number
            df = df.astype({"time_setup": str, "time_done": str})
            return df.to_dict("records")

    def get_symbol_tick_info(self, symbol_pair):
        # attempt to enable the display of the GBPUSD in MarketWatch
        selected = mt5.symbol_select(symbol_pair, True)
        if not selected:
            print(f"Failed to select {symbol_pair}")
        else:
            symbol_info_tick_dict = mt5.symbol_info_tick(symbol_pair)._asdict()
            return symbol_info_tick_dict

    def close_connection(self):
        mt5.shutdown()
