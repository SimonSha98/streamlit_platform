import config
import alpaca_trade_api as tradeapi
import mysql.connector

connection = mysql.connector.connect(
  host=config.DB_HOST,               #hostname
  user=config.DB_USER,                   # the user who has privilege to the db
  passwd=config.DB_PASS,               #password for user
  database=config.DB_NAME,               #database name
  #auth_plugin = 'mysql_native_password',
)
cursor = connection.cursor()

api = tradeapi.REST(config.API_KEY, config.API_SECRET, base_url=config.API_URL)

assets = api.list_assets()

for asset in assets:
    print(f"Inserting stock {asset.name} {asset.symbol}")
    cursor.execute("""
        INSERT INTO stock (name, symbol, exchange)
        VALUES (%s, %s, %s)
    """, (asset.name, asset.symbol, asset.exchange))

connection.commit()
