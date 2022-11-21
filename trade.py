import pandas as pd
import yfinance as yf
import mplfinance as mpf
import numpy as np

class trade:
    def __init__(self):
        #self.stockName = stockName
        self.name = 'default'

    def create_charts(self, stockName):
        data = yf.download(tickers=f'{stockName}', period='1d', interval='1m')
        customstyle = mpf.make_mpf_style(base_mpf_style='yahoo',
                                         y_on_right=False,
                                         facecolor='w')
        mpf.plot(data,
                 type='candle',
                 title=f'${stockName} price',
                 ylabel='Price ($USD)',
                 xlabel='Time',
                 mav=(20),
                 addplot=mpf.make_addplot(
                     data.Volume, type='bar', panel=1, ylabel='Volume', y_on_right=False),
                 tight_layout=True,
                 style=customstyle,
                 savefig='chart.png')

    def compare_stocks(self, stockName1, stockName2):
        stock1 = yf.download(f'{stockName1}', period='1d', interval='1m')
        stock2 = yf.download(f'{stockName2}', period='1d', interval='1m')
        customstyle = mpf.make_mpf_style(base_mpf_style='yahoo',
                                         y_on_right=False,
                                         facecolor='w')
        adds = [mpf.make_addplot(stock1.Volume, type='bar', panel=1, ylabel='Volume', y_on_right=False),
                mpf.make_addplot(stock2, type='candle', panel=2,
                                 ylabel=f'\${stockName2} (\$USD)', mav=(5)),
                mpf.make_addplot(stock2.Volume, type='bar', panel=3, ylabel='Volume', y_on_right=False)]

        mpf.plot(stock1,
                 type='candle',
                 title=f'\${stockName1} vs \${stockName2}',
                 ylabel=f'\${stockName1} (\$USD)',
                 xlabel='Time',
                 mav=(5),
                 addplot=adds,
                 tight_layout=True,
                 style=customstyle,
                 savefig='chart.png')

    def EOD(self, stockName):
        data = yf.download(tickers=f'{stockName}', period='1d')
        df = pd.DataFrame(data)
        adj = df['Adj Close'][0]
        return f'EOD update on ${stockName}\n-Date: {df.index[0].date()}\n-Open: {df.Open[0]}\n-High: {df.High[0]}\n-Low: {df.Low[0]}\n-Close: {df.Close[0]}\n-Adj Close: {adj}\n-Volume: {df.Volume[0]}'

    def bollinger(self, stockName):
        df = yf.download(tickers=f'{stockName}', period='1d', interval='1m')
        data = pd.DataFrame(df)
        customstyle = mpf.make_mpf_style(base_mpf_style='yahoo',
                                         y_on_right=False,
                                         facecolor='w')

        data['Middle Band'] = data['Close'].rolling(window=21).mean()
        data['Upper Band'] = data['Middle Band'] + 2*data['Close'].rolling(window=21).std()
        data['Lower Band'] = data['Middle Band'] - 2*data['Close'].rolling(window=21).std()
        data['Percent Band'] = (data['Close'] - data['Lower Band'])/(data['Upper Band'] - data['Lower Band'])

        def bollingerBandStrategy(data, lower_bb, upper_bb, open):
            buy_price = []
            sell_price = []
            bb_signal = []
            signal = False
        
            for i in range(len(data)):
                if lower_bb[i] > ((data[i] + open[i])/2):
                    if  not signal:
                        buy_price.append(data[i])
                        sell_price.append(np.nan)
                        signal = True
                        bb_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        bb_signal.append(0)
                elif upper_bb[i] < ((data[i] + open[i])/2):
                    if signal:
                        buy_price.append(np.nan)
                        sell_price.append(data[i])
                        signal = False
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

        buy_price, sell_price, bb_signal = bollingerBandStrategy(data['Close'], data['Lower Band'], data['Upper Band'], data['Open'])

        apd = [mpf.make_addplot(data['Upper Band'], color = 'blue'),
            mpf.make_addplot(data['Lower Band'], color = 'blue'),
            mpf.make_addplot(buy_price, type = 'scatter',markersize=200,marker='^', color = 'green'),                                                                        
            mpf.make_addplot(sell_price, type = 'scatter',markersize=200,marker='^', color = 'red')]

        mpf.plot(data,
                type='candle',
                title=f'${stockName} price',
                ylabel='Price ($USD)',
                xlabel='Time',
                figscale = 1.25,
                addplot=apd, 
                tight_layout=True,
                style=customstyle,
                savefig='chart.png')


