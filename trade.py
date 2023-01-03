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
                                 ylabel=f'\${stockName2} (\$USD)'),
                mpf.make_addplot(stock2.Volume, type='bar', panel=3, ylabel='Volume', y_on_right=False)]

        mpf.plot(stock1,
                 type='candle',
                 title=f'\${stockName1} vs \${stockName2}',
                 ylabel=f'\${stockName1} (\$USD)',
                 xlabel='Time',
                 addplot=adds,
                 tight_layout=True,
                 style=customstyle,
                 savefig='chart.png')

    def EOD(self, stockName):
        data = yf.download(tickers=f'{stockName}', period='1d')
        df = pd.DataFrame(data)
        adj = df['Adj Close'][0]
        return f'EOD update on ${stockName}\n-Date: {df.index[0].date()}\n-Open: {df.Open[0]}\n-High: {df.High[0]}\n-Low: {df.Low[0]}\n-Close: {df.Close[0]}\n-Adj Close: {adj}\n-Volume: {df.Volume[0]}'

    def calcBollAndRsi(data):
        data['Percent Change'] = data['Close'].pct_change()
        data['Buy&Hold returns'] = (1+data['Percent Change']).cumprod()
        data['Middle Band'] = data['Close'].rolling(window=21).mean()
        data['Upper Band'] = data['Middle Band'] + \
            2*data['Close'].rolling(window=21).std()
        data['Lower Band'] = data['Middle Band'] - \
            2*data['Close'].rolling(window=21).std()
        data['Upmove'] = data['Percent Change'].apply(
            lambda x: x if x > 0 else 0)
        data['Downmove'] = data['Percent Change'].apply(
            lambda x: abs(x) if x < 0 else 0)
        data['Avg Up'] = data['Upmove'].ewm(span=19).mean()
        data['Avg Down'] = data['Downmove'].ewm(span=19).mean()
        data['RS'] = data['Avg Up']/data['Avg Down']
        data['RSI'] = data['RS'].apply(lambda x: 100-(100/(x+1)))

    def bollingerBandRsiStrategy(data):
        conditions = [(data['Close'] < data['Lower Band']) & (data['RSI'] < 30),
                      (data['Close'] > data['Upper Band']) & (data['RSI'] > 70)]
        choices = ['Buy', 'Sell']
        data['Signals'] = np.select(conditions, choices)
        data['Signals'] = data['Signals'].shift(1)
        data.dropna(inplace=True)
        buyDate, sellDate = [], []
        buyPrice, sellPrice = [], []
        signal = []
        position = False

        for i in range(len(data)):
            if not position and data['Signals'][i] == 'Buy':
                buyDate.append(data.index[i])
                buyPrice.append(data.Open[i])
                sellPrice.append(np.nan)
                position = True
            elif position and data['Signals'][i] == 'Sell':
                sellDate.append(data.index[i])
                sellPrice.append(data.Open[i])
                buyPrice.append(np.nan)
                position = False
            else:
                buyPrice.append(np.nan)
                sellPrice.append(np.nan)
            if not position:
                signal.append(0)
            else:
                signal.append(1)

        return buyDate, sellDate, buyPrice, sellPrice, signal

    def calcProfits(data, buyDate, sellDate):
        buys = data.loc[buyDate].Open
        sells = data.loc[sellDate].Open
        profits = (pd.Series([(sell - buy) / buy for sell,
                   buy in zip(sells, buys)])+1).prod()-1
        return profits

    def bollinger(self, stockName, interval):
        try:
            data = yf.Ticker(f'{stockName}').history(period='1y')
            if data.empty:
                raise Exception
        except:
            return 'Not a real stock'

        if interval == '1d':
            df = yf.download(tickers=f'{stockName}',
                             period='1d', interval='1m')
            data = pd.DataFrame(df)
        elif interval == '1mo':
            df = yf.download(tickers=f'{stockName}',
                             period='1mo', interval='15m')
            data = pd.DataFrame(df)
        elif interval == '1y':
            df = yf.download(tickers=f'{stockName}',
                             period='1y', interval='1d')
            data = pd.DataFrame(df)
        elif interval == '2y':
            df = yf.download(tickers=f'{stockName}',
                             period='2y', interval='1d')
            data = pd.DataFrame(df)
        elif interval == 'max':
            df = yf.download(tickers=f'{stockName}',
                             period='max', interval='1d')
            data = pd.DataFrame(df)
        else:
            return 'Interval unavailable'

        customstyle = mpf.make_mpf_style(base_mpf_style='yahoo',
                                         y_on_right=False,
                                         facecolor='w')

        trade.calcBollAndRsi(data)

        buyDate, sellDate, buyPrice, sellPrice, signal = trade.bollingerBandRsiStrategy(
            data)

        data['Position'] = signal
        data['Strategy returns'] = (
            1 + data['Position'] * data['Percent Change']).cumprod()

        profits = trade.calcProfits(data, buyDate, sellDate) * 100

        upper = np.asarray(data['Upper Band'])
        lower = np.asarray(data['Lower Band'])
        buyAndHold = np.asarray(data['Buy&Hold returns'])
        stratReturns = np.asarray(data['Strategy returns'])
        apd = [mpf.make_addplot(upper, color='blue'),
               mpf.make_addplot(lower, color='blue'),
               mpf.make_addplot(buyPrice, type='scatter',
                                markersize=200, marker='^', color='green'),
               mpf.make_addplot(sellPrice, type='scatter',
                                markersize=200, marker='v', color='red'),
               mpf.make_addplot(buyAndHold,
                                type='line', panel=1, ylabel='Performance', color='red'),
               mpf.make_addplot(stratReturns, type='line', panel=1, ylabel='Performance', color='green')]

        mpf.plot(data,
                 type='candle',
                 title=f'${stockName} price',
                 ylabel='Price ($USD)',
                 xlabel='Time',
                 figscale=1.25,
                 addplot=apd,
                 tight_layout=True,
                 style=customstyle,
                 savefig='chart.png')

        returns = str(
            round(profits, 2))
        return f'Legend for performance graph:\nGreen: Bollinger strategy\nRed: (default) Buy and hold strategy\nCumulative returns: {returns}%'
