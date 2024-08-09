import datetime as dt
import matplotlib.pyplot as plt  
import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')
plt.style.use('fivethirtyeight')

def bollinger_bands(data, window_size = 30): #Bollinger Bands Function
    ma_30 = data['Close'].rolling(window = window_size).mean()
    std_30 = data['Close'].rolling(window = window_size).std()
    data['UpperBand'] = ma_30 + (2 * std_30)
    data['LowerBand'] = ma_30 - (2 * std_30)
    return data

def RSI(data, window = 13): #RSI function
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean() 
    RS = avg_gain / avg_loss
    RSIndex = 100 - (100 / (1 + RS))
    data['RSI'] = RSIndex
    data['Overbought'] = 70
    data['Oversold'] = 30
    return data

#Strategy Idea:
#Buy: If the close price is below 30 RSI and below lower band, the stock is undervalued
#Sell: If the close price is above 70 RSI and above upper band, the stock is overvalued
def strategy(data):
    position = 0
    buy_price = []
    sell_price = []
    for i in range(0, len(data)):
        if data['Close'][i] < data['LowerBand'][i] and data['RSI'][i] < 30 and position == 0:
            position = 1
            buy_price.append(data['Close'][i])
            sell_price.append(np.nan)
        elif data['Close'][i] > data['UpperBand'][i] and data['RSI'][i] > 70 and position == 1:
            position = 0
            sell_price.append(data['Close'][i])
            buy_price.append(np.nan)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
    return(buy_price, sell_price)

ticker = input("Choose a Ticker \n").upper()
data = yf.download(ticker, period = '3y')
data = bollinger_bands(data)
data = RSI(data)
buy_price, sell_price = strategy(data)
data['Buy'] = buy_price
data['Sell'] = sell_price  

fig, ax = plt.subplots(figsize=(16,8))
plt.title(ticker + ' Bollinger + RSI')
plt.ylabel('Price')
plt.xlabel('Date')
ax.plot(data.index, data['Close'], label = 'Close Price', color = 'black', linewidth = 1.5)
ax.plot(data['UpperBand'], label = 'Upper Band', alpha = 0.25, color = 'green', linewidth = 1)
ax.plot(data['LowerBand'], label = 'Lower Band', alpha = 0.25, color = 'red', linewidth = 1)
ax.fill_between(data.index, data['UpperBand'], data['LowerBand'], alpha = 0.1, color = 'yellow')
ax.scatter(data.index, data['Buy'], label = 'Buy', color = 'green', alpha = 1, marker = '^', linewidth = 2)
ax.scatter(data.index, data['Sell'], label = 'Sell', color = 'red', alpha = 1, marker = 'v', linewidth = 2)
ax.legend()
plt.show()

buy_signals = data[data['Buy'] > 0].index
sell_signals = data[data['Sell'] > 0].index
# Calculate returns for each trade
returns = []
for buy, sell in zip(buy_signals, sell_signals):
    buy_price = data.loc[buy, 'Close']
    sell_price = data.loc[sell, 'Close']
    trade_return = (sell_price - buy_price) / buy_price
    returns.append(trade_return)

# Calculate cumulative return
cumulative_return = np.prod([1 + r for r in returns]) - 1
cumulative_return_percentage = round(cumulative_return * 100, 2)
print("Cumulative Return: " + str(cumulative_return_percentage) + "%")

# Calculate total number of days in the dataset
total_days = (data.index[-1] - data.index[0]).days

# Calculate annualized return
annualized_return = (1 + cumulative_return) ** (365 / total_days) - 1
annualized_return_percentage = round(annualized_return * 100, 2)
print("Annualized Return: " + str(annualized_return_percentage) + "%")