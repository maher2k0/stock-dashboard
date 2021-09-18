# This app is for educational purpose only. Insights gained is not financial advice. Use at your own risk!
from pandas.core.frame import DataFrame
import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
import time
import csv
import plotly.express as px
import altair as alt
import urllib

apikey = 'ZZLZTMNIX42MFKZK'
#---------------------------------#
# New feature (make sure to upgrade your streamlit library)
# pip install --upgrade streamlit

#---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
#---------------------------------#

#===========================================================================================================================================
#loading bar
my_bar = st.progress(0)
for percent_complete in range(100):
      time.sleep(0.1)
      my_bar.progress(percent_complete+1)
#===========================================================================================================================================

# Logo
#image = Image.open('cuirs.png')
#st.image(image, width = 50)

#st.title('Stock screener')
st.markdown("""
This app retrieves stock prices and data from **Yahoo Finance** and **Alpha Advantage**!
""")

#---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.beta_columns((2,1))

#===============================================================================================================================================
# Sidebar + Main panel
col1.header('Input Options')

## Sidebar - Currency price unit
user_input = col1.text_input("ticker", value='TSLA')
input_interval = col1.selectbox('Select interval', ('1d', '5d', '1mo','3mo'), index = 0)
start_date = col1.date_input('select start date', value = datetime(2016,10,12))
end_date = col1.date_input('select end date')
col1.subheader('Technical indicators')
input_indicator_interval = col1.selectbox('Select indicator interval for SMA & EMA', ('daily','weekly','monthly'))
#===============================================================================================================================================

# Plot Closing Price of Query Symbol
def price_plot():
  df = pd.DataFrame(dataa.Close)
  df['Date'] = df.index
  fig, ax = plt.subplots(figsize=(10,6))
  plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
  plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
  plt.xticks(rotation=90)
  plt.title(user_input, fontweight='bold')
  plt.xlabel('Date', fontweight='bold')
  plt.ylabel('Closing Price', fontweight='bold')

  return col2.pyplot(fig)

#===============================================================================================================================================

stock = yf.Ticker(user_input)
try:
  col2.title(stock.info['longName'])
  expander_bar = col2.beta_expander("About the company")
  expander_bar.markdown(stock.info['longBusinessSummary'])

#==============================================================================================================================================
#data scraping 

  dataa = yf.download(
      tickers = user_input,
      #period = "max",
      start = start_date,
      end = end_date,
      interval = input_interval,
      group_by = "ticker",
      auto_adjust = True,
      prepost = True,
      threads = True,
      proxy = None
  )

  df2 = pd.DataFrame(dataa.Close)
  col2.header('Stock Closing Price')
  col2.line_chart(df2)

except KeyError:
  st.error('Please enter a valid ticker symbol')



# Web scraping of CoinMarketCap data
@st.cache
def load_data():
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings:
      coins[str(i['id'])] = i['slug']

    coin_name = []
    coin_symbol = []
    marketCap = []
    percentChange1h = []
    percentChange24h = []
    percentChange7d = []
    price = []
    volume24h = []

    for i in listings:
      coin_name.append(i['slug'])
      coin_symbol.append(i['symbol'])
      price.append(i['quote'][currency_price_unit]['price'])
      percentChange1h.append(i['quote'][currency_price_unit]['percentChange1h'])
      percentChange24h.append(i['quote'][currency_price_unit]['percentChange24h'])
      percentChange7d.append(i['quote'][currency_price_unit]['percentChange7d'])
      marketCap.append(i['quote'][currency_price_unit]['marketCap'])
      volume24h.append(i['quote'][currency_price_unit]['volume24h'])

    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'marketCap', 'percentChange1h', 'percentChange24h', 'percentChange7d', 'price', 'volume24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percentChange1h'] = percentChange1h
    df['percentChange24h'] = percentChange24h
    df['percentChange7d'] = percentChange7d
    df['marketCap'] = marketCap
    df['volume24h'] = volume24h
    return df


#=================================================================================================================================================

def price_plot_interactive():
    df = pd.DataFrame(dataa.Close)
    df['Date'] = df.index
    fig3 = go.Figure(data=[go.Candlestick(x=df['Date'],
           open = dataa['Open'],
           high = dataa['High'],
           low = dataa['Low'],
           close=dataa['Close'])])
    return col2.plotly_chart(fig3,use_container_width=True)


#price_plot()
col2.subheader('Candlestick plot')
try:
  price_plot_interactive()
except NameError:
  st.error('Please select a valid start and end date')


#===============================================================================================================================================
col2.subheader('Stock data')
col2.dataframe(dataa)

# Download CSV data
@st.cache
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(dataa), unsafe_allow_html=True)


#========================================================================================================================================================
#technical indicators
@st.cache
def SMA():
  API_URL = "https://www.alphavantage.co/query"
  data = { "function": "SMA",
  "symbol": user_input,
  "interval": input_indicator_interval,
  "time_period" : "10",
  "series_type" : 'open',
  "datatype": "json",
  "apikey": "ZZLZTMNIX42MFKZK" }

  r = requests.get(API_URL,data).json()
  data_sma = pd.DataFrame.from_dict(r['Technical Analysis: SMA'], orient= 'index').sort_index(axis=1)
  data_sma['Date'] = data_sma.index
  data_sma['SMA'] = pd.to_numeric(data_sma['SMA'], downcast = 'float')
  return data_sma

@st.cache
def EMA():
  API_URL = "https://www.alphavantage.co/query"
  data = { "function": "EMA",
  "symbol": user_input,
  "interval": input_indicator_interval,
  "time_period" : "10",
  "series_type" : 'open',
  "datatype": "json",
  "apikey": "ZZLZTMNIX42MFKZK" }

    #url = 'https://www.alphavantage.co/query/'
  r = requests.get(API_URL,data).json()
  data_ema = pd.DataFrame.from_dict(r['Technical Analysis: EMA'], orient= 'index').sort_index(axis=1)
  data_ema['Date'] = data_ema.index
  data_ema['EMA'] = pd.to_numeric(data_ema['EMA'], downcast = 'float')
  return data_ema




if col1.button('Show interactive SMA/EMA plot'):
  df_ema = EMA()
  df_sma = SMA()

  fig_sma = px.line(x=df2.index,y=df2['Close'], title = user_input + ' Technical indicator chart')
  fig_sma.add_scatter(x=df_sma["Date"],y=df_sma["SMA"], name = 'SMA')
  fig_sma.add_scatter(x=df_ema["Date"],y=df_ema["EMA"], name = 'EMA' )

  fig_sma.update_layout(
    xaxis_title = '',
    yaxis_title = 'Price (USD)',
    legend_title = 'Indicators'
  )

  #fig_sma.update_xaxes(showgrid=False)
  #fig_sma.update_yaxes(showgrid=False)

  col1.pyplot(fig_sma.show())
col1.text('built by Maher')
#========================================================================================================================================================
#income statement, balance sheet, cash flow, 

@st.cache
def balance_sheet():
  API_URL = "https://www.alphavantage.co/query"
  data = { "function": "BALANCE_SHEET",
  "symbol": user_input,
  "datatype": "json",
  "apikey": apikey}
  
  r = requests.get(API_URL,data)
  data_balancesheet = r.json()
  balance_sheet_df = pd.DataFrame(data = data_balancesheet['annualReports'])

  return balance_sheet_df

@st.cache
def cash_flow():
  API_URL = "https://www.alphavantage.co/query"
  data = { "function": "CASH_FLOW",
  "symbol": user_input,
  "datatype": "json",
  "apikey": apikey}
  
  r = requests.get(API_URL,data)
  data_cashflow = r.json()
  cash_flow_df = pd.DataFrame(data = data_cashflow['annualReports'])

  return cash_flow_df

@st.cache
def income_statement():
  API_URL = "https://www.alphavantage.co/query"
  data = { "function": "INCOME_STATEMENT",
  "symbol": user_input,
  "datatype": "json",
  "apikey": apikey}
  
  r = requests.get(API_URL,data)
  data_incomestatement = r.json()
  income_statement_df = pd.DataFrame(data = data_incomestatement['annualReports'])

  return income_statement_df

balance_sheet_df = balance_sheet()
cash_flow_df = cash_flow()
income_statement_df = income_statement()

col2.header('Fundamental Data')

col2.subheader("Balance Sheet")
col2.dataframe(balance_sheet_df)
col2.markdown(filedownload(balance_sheet_df), unsafe_allow_html=True)

col2.subheader("Cash Flow")
col2.dataframe(cash_flow_df)
col2.markdown(filedownload(cash_flow_df), unsafe_allow_html=True)

col2.subheader("Income Statement")
col2.dataframe(income_statement_df)
col2.markdown(filedownload(income_statement_df), unsafe_allow_html=True)

#========================================================================================================================================================
#column 3

my_dict = stock.info
df = pd.DataFrame(list(my_dict.items()),columns = ['descriptor','value']) 
df.set_index("descriptor", inplace = True)


#137,136,148,139,132,83,127,26
#all numerical info
def stock_info(): 
    cutdown_info_df = df.loc[['previousClose','open','bid','ask','volume','beta','earningsGrowth','marketCap']]
    return cutdown_info_df

#all info which has a string as value - sector, city country, industry
def more_stock_info():
    word_info = df.loc[['sector','city','country','industry']]
    return word_info

col3.subheader('Company Overview')
col3.write(more_stock_info())
col3.write(stock_info())

stock_dict = stock.info
new_stock_dict = {}
for x,y in my_dict.items():
  if (type(y) == int) or (type(y) == float) :
    new_stock_dict[x] = y
  else:
    continue

if col3.button('Show more info'):
  col3.dataframe((pd.DataFrame([new_stock_dict])).transpose())


@st.cache
def earnings_calendar():
  API_URL = "https://www.alphavantage.co/query?"
  data = { "function": "EARNINGS_CALENDAR",
  "symbol": user_input,
  "horizon": "3month",
  "apikey": apikey}

  full_URL = API_URL + urllib.parse.urlencode(data)
  with requests.Session() as s:
    download = s.get(full_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)

    earnings_calendar_list =[]
    for row in my_list:
        earnings_calendar_list.append(row)
  df = pd.DataFrame(earnings_calendar_list[1:])
  df.columns = earnings_calendar_list[0]

  return df

col3.subheader('Earnings Calendar')
col3.dataframe(earnings_calendar())



#--------------------------------#
