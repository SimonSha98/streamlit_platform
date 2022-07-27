import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import arch
import pmdarima
import matplotlib.pyplot as plt
import time

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title('Stock Forecast App')


#stocks = ('GOOG', 'AAPL', 'MSFT', 'GME')
#selected_stock = st.selectbox('Select dataset for prediction', stocks)

st.subheader('Input stock ticker here')
selected_stock = st.text_input(label = "ticker", value='MSFT', max_chars=None, key=None, type='default')


@st.cache
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data


data = load_data(selected_stock)
my_bar = st.progress(0)
for percent_complete in range(100):
     time.sleep(0.001)
     my_bar.progress(percent_complete + 1)
st.success("Complete!")

st.subheader('Raw data')
st.write(data.tail())

# Plot raw data
def plot_raw_data():
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
	fig.layout.update(title_text=f'Time Series data of {selected_stock}', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)

plot_raw_data()

# Predict forecast with Prophet.
df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

n_years = st.number_input('Insert number of years you want to forecast', step = 1)
period = n_years * 365


m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)


# fit ARIMA on returns
#arima_model_fitted = pmdarima.auto_arima(df_train[['y']])
#p, d, q = arima_model_fitted.order

#fig, ax = plt.subplots()
#ax.plot(arima_model_fitted.predict(n_periods=period))
#st.pyplot(fig)


# Show and plot forecast
st.subheader(f'Forecast closing price of {selected_stock} for {n_years} year(s)')
st.write(forecast.tail())

fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)
