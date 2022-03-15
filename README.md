### Description:
The purpose of this script is scraper different types of data from MetaTrader5 tool and populate in database accordingly
Download Link: https://cloud.go.pepperstone.com/go-to?page=pepperstone-uk-mt5-win

### PreReqs:
* Python: 3.6+

### Setup:
* create a virtual environment: `virtualenv -p /usr/bin/python3 env` (Optional)
* activate the environemnt: `source ./env/bin/activate` (Optional when you don't need first step)
* install requirements: `pip install -r requirements.txt`
* Edit `utils.py` file to update the Database settings according to yours
* Following are the Database variables which needs to be updated
```
DB_HOST = "localhost"
DB_USERNAME = "testUsername"
DB_PASSWORD = "testPassword"
DB_DATABASE = "testDatabase"
DB_TABLE = "testTable"
```
* Create a json file with name `accounts.json` and put multiple accounts in following format:
```
[
    {
        "account_number": 123,
        "password": "pwd1",
        "server": "test-server-1",
        "email": "abc@test.com" 
    },
    {
        "account_number": 456,
        "password": "pwd2",
        "server": "test-server-2",
        "email": "abc@test.com" 
    }
]
```

### Run:
* Command to run scraper: `python main.py`

### Note:
*  `requirements.txt` file contains the list of packages that are required to install.
* After processing, extracted information will be populated into database tables accordingly.
