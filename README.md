### Description:
The purpose of this script is scraper different types of data from MetaTrader5 tool and populate in database accordingly

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

### Run:
* Command to run scraper: `python main.py`

### Note:
*  `requirements.txt` file contains the list of packages that are required to install.
* After processing, extracted information will be populated into database tables accordingly.
