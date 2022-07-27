import streamlit as st
import pandas as pd
import numpy as np
import requests
import tweepy
import config
import mysql.connector
import plotly.graph_objects as go

from datetime import date
import datetime
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import time

client = tweepy.Client(consumer_key = config.TWITTER_CONSUMER_KEY,
                        consumer_secret = config.TWITTER_CONSUMER_SECRET,
                        access_token = config.TWITTER_ACCESS_TOKEN,
                        access_token_secret = config.TWITTER_ACCESS_TOKEN_SECRET,
                        bearer_token = config.BEARER_TOKEN,
                        wait_on_rate_limit = True)

connection = mysql.connector.connect(
  host=config.DB_HOST,               #hostname
  user=config.DB_USER,                   # the user who has privilege to the db
  passwd=config.DB_PASS,               #password for user
  database=config.DB_NAME,               #database name
  #auth_plugin = 'mysql_native_password',
)
cursor = connection.cursor()

option = st.sidebar.selectbox("Which Dashboard?", ('twitter', 'wallstreetbets', 'stocktwits', 'chart'), 1)

st.header(option)

if option == 'twitter':
    for username in config.TWITTER_USERNAMES:
        user = client.get_user(username = username, user_fields = ['profile_image_url'])
        tweets = client.get_users_tweets(user.data.id)

        st.subheader(username)
        st.image(user.data.profile_image_url)

        for tweet in tweets.data:
            if '$' in tweet.text:
                words = tweet.text.split(' ')
                for word in words:
                    if word.startswith('$') and word[1:].isalpha(): #check if word is a stock ticker
                        symbol = word[1:]
                        st.write(symbol)
                        st.write(tweet.text)
                        st.image(f"https://finviz.com/chart.ashx?t={symbol}")


if option == 'chart':
    symbol = st.sidebar.text_input("Symbol", value='MSFT', max_chars=None, key=None, type='default')

    START = st.sidebar.date_input("Start Date", datetime.date(2019, 1, 1))
    TODAY = date.today().strftime("%Y-%m-%d")

    @st.cache
    def load_data(ticker):
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data


    data = load_data(symbol)

    st.subheader(symbol.upper())

    fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=symbol)])

    fig.update_xaxes(type='category')
    fig.update_layout(height=800)

    st.plotly_chart(fig, use_container_width=True)
    st.write(data)


    #stock closing price prediction using prophet
    df_train = data[['Date','Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    n_days = st.sidebar.number_input('Insert number of days you want to forecast', value = 1, step = 1)

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=n_days)
    forecast = m.predict(future)

    st.subheader(f'Forecast closing price of {symbol} for {n_days} day(s)')
    st.write(forecast.tail())

    # fig1 = plot_plotly(m, forecast)
    # st.plotly_chart(fig1)
    predicted = forecast[-n_days-10:]

    actual = data.tail(10)

    def plot_raw_data():
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=actual['Date'], y=actual['Close'], name="stock_close"))
        fig2.add_trace(go.Scatter(x=predicted['ds'], y=predicted['trend'], name="predicted"))
        fig2.layout.update(title_text=f'prediction {symbol} daily closing price', xaxis_rangeslider_visible=True)
        st.plotly_chart(fig2)

    plot_raw_data()


if option == 'wallstreetbets':
    num_days = st.sidebar.slider('Number of days', 1, 30, 1)

    cursor.execute("""
        SELECT COUNT(*) AS num_mentions, symbol
        FROM mention JOIN stock ON stock.id = mention.stock_id
        WHERE date(dt) >= CURRENT_DATE() - INTERVAL %s DAY
        GROUP BY stock_id, symbol
        HAVING COUNT(*) >= 2
        ORDER BY num_mentions DESC
    """, (num_days,))

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)

    fig = go.Figure()
    fig.add_trace(go.Bar(x = df['symbol'], y = df['num_mentions']))
    fig.update_xaxes(title_text="stock ticker")
    fig.update_yaxes(title_text="number of mentions")
    fig.update_layout(height=800)
    fig.update_layout(width=1200)
    st.plotly_chart(fig)


if option == 'stocktwits':
    symbol = st.sidebar.text_input("Symbol", value='MSFT', max_chars=5)

    r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")

    data = r.json()

    for message in data['messages']:
        st.image(message['user']['avatar_url'])
        st.write(message['user']['username'])
        st.write(message['created_at'])
        st.write(message['body'])
