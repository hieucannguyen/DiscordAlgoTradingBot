import pandas as pd
import yfinance as yf
import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as m_img
import trade

df = yf.download(tickers='AAPL', period='1d', interval='1m')
data = pd.DataFrame(df)
customstyle = mpf.make_mpf_style(base_mpf_style='yahoo',
                                 y_on_right=False,
                                 facecolor='w')

data['Middle Band'] = data['Close'].rolling(window=21).mean()
data['Upper Band'] = data['Middle Band'] + 2*data['Close'].rolling(window=21).std()
data['Lower Band'] = data['Middle Band'] - 2*data['Close'].rolling(window=21).std()
data['Percent Band'] = (data['Close'] - data['Lower Band'])/(data['Upper Band'] - data['Lower Band'])
print(data)

def implement_bb_strategy(data, lower_bb, upper_bb, open):
    buy_price = []
    sell_price = []
    bb_signal = []
    signal = -1
    
    for i in range(len(data)):
        if lower_bb[i] > ((data[i] + open[i])/2):
            if signal != 1:
                buy_price.append(data[i])
                sell_price.append(np.nan)
                signal = 1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        elif upper_bb[i] < ((data[i] + open[i])/2):
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(data[i])
                signal = -1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            bb_signal.append(0)
            
    return buy_price, sell_price, bb_signal

buy_price, sell_price, bb_signal = implement_bb_strategy(data['Close'], data['Lower Band'], data['Upper Band'], data['Open'])
tcdf = data[['Upper Band', 'Lower Band']]
#data1 = yf.download(tickers='GOOG', period='1d', interval='1m')
apd = [mpf.make_addplot(tcdf), mpf.make_addplot(buy_price, type = 'scatter',markersize=200,marker='^'), mpf.make_addplot(sell_price, type = 'scatter',markersize=200,marker='^'),
mpf.make_addplot(data.Volume, type='bar', panel=1, ylabel='Volume', y_on_right=False)]

mpf.plot(data,
         type='candle',
         title='$AAPL price',
         ylabel='Price ($USD)',
         xlabel='Time',
         figscale = 1.25,
         addplot=apd, 
         tight_layout=True,
         style=customstyle)

mpf.show()
