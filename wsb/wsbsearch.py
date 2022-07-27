from psaw import PushshiftAPI
import config
import datetime
import mysql.connector

connection = mysql.connector.connect(
  host=config.DB_HOST,               #hostname
  user=config.DB_USER,                   # the user who has privilege to the db
  passwd=config.DB_PASS,               #password for user
  database=config.DB_NAME,               #database name
  #auth_plugin = 'mysql_native_password',
)
cursor = connection.cursor()
cursor.execute("""
    SELECT * FROM stock
""")
rows = cursor.fetchall()

stocks = {}
for row in rows:
    stocks['$' + row[1]] = row[0]


api = PushshiftAPI()

start_time = int(datetime.datetime(2022, 7, 1).timestamp())

submissions = api.search_submissions(after=start_time,
                                     subreddit='wallstreetbets',
                                     filter=['url','author', 'title', 'subreddit'])






for submission in submissions:
    words = submission.title.split()
    cashtags = list(set(filter(lambda word: word.lower().startswith('$'), words)))

    if len(cashtags) > 0:

        print(cashtags)
        print(submission.title)

        for cashtag in cashtags:
            if cashtag in stocks:
                submitted_time = datetime.datetime.fromtimestamp(submission.created_utc).isoformat()

                try:
                    cursor.execute("""
                        INSERT INTO mention (dt, stock_id, message, source, url)
                        VALUES (%s, %s, %s, 'wallstreetbets', %s)
                    """, (submitted_time, stocks[cashtag], submission.title, submission.url))

                    connection.commit()
                except Exception as e:
                    print(e)
                    connection.rollback()
