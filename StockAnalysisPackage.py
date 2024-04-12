# import neccessary packages
import pandas as pd
import yfinance as yf
from datetime import datetime, date
import plotly.graph_objects as go

import warnings
warnings.filterwarnings('ignore')

class StockAnalysis:
    
    """
    StockAnalysis class is used to analyze stocks using yfinance package.
    There are multiple functions for use along with various checks in place to ensure smooth running of the package.

    Each function has individual comments for their use and outputs.
    """

    def __init__(self, symbol, start_date, end_date):

      """
      In the initialization of our package class, three essential input parameters—namely, 'symbol', 'start_date,' and 'end_date' are required from the user upon creating an object of this class. These user-provided values are stored within the class and are subsequently utilized by various functions for their respective tasks. The class also initializes the 'stock_data' variable, which serves as a storage container for the fetched data in the form of a dataframe, to be utilized by subsequent functions after the 'fetch_stock_data' function is invoked.
      
      Attributes: 
        symbol: A string value representing the ticker or stock name in the yahoo finance market.
        start_date: A string value in the 'yyyy-mm-dd' format, determining the commencement date from which the data is to be fetched.
        end_date: A string value in the 'yyyy-mm-dd' format, indicating the termination date until which the data should be fetched.
      
      Return: Object
      """

      self.symbol = symbol
      self.start_date = start_date
      self.end_date = end_date
      self.stock_data = None

    def fetch_stock_data(self):

      self.ticker = yf.Ticker(self.symbol)
      info = None
      today_date = date.today()

      try:
        info = self.ticker.info
        quoteType = info['quoteType']

        if quoteType != 'EQUITY':   # Check if the ticker mentioned is a stock ticker or not
          raise Exception("Symbol Error: Ticker does not belong to stock/equity")
        else:
          list_date = datetime.fromtimestamp(info['firstTradeDateEpochUtc']).strftime('%Y-%m-%d')
          if self.start_date < list_date:   # Check if the start date is before the list date of stock
            raise Exception("Date Error: Start Date before stock List Date")
          elif self.end_date > str(today_date):   # Check if the end date is after today's date
            raise Exception("Date Error: End Date after today's date")
          else:
            self.stock_data = yf.download(self.symbol, start=self.start_date, end=self.end_date)
            self.stock_data["Date"] = self.stock_data.index
            self.stock_data = self.stock_data[["Date", "Open", "High","Low", "Close", "Adj Close", "Volume"]]
            self.stock_data.reset_index(drop=True, inplace=True)
            print("Stock data fetched successfully.")
            print(self.stock_data.info())
      except Exception as e:
        if "404 Client Error" in str(e):
          print("Ticker {} does not exist.".format(self.symbol))
        elif "Date" in str(e):
          print(e)
        elif "Symbol" in str(e):
          print(e)

    def visualize_candlestick(self, plot_start = None, plot_end = None):

      plot_start = plot_start or self.start_date
      plot_end = plot_end or self.end_date

      try:
        if plot_start < self.start_date:
          raise Exception("Date Error: Plot Start date provided is before the Data Fetch start date")
        elif plot_end > self.end_date:
          raise Exception("Date Error: Plot End date provided is after the Data Fetch end date")
        else:
          plot_data = self.stock_data[(self.stock_data['Date'] >= plot_start) & (self.stock_data['Date'] <= plot_end)]

          fig = go.Figure(data=[go.Candlestick(x=plot_data['Date'],open=plot_data['Open'],\
                                               high=plot_data['High'],low=plot_data['Low'], close=plot_data['Close'])])
          fig.update_layout(xaxis_rangeslider_visible=False)
          fig.show()
      except Exception as e:
        print(e)

    def calculate_moving_average(self, window = 21):
      self.window = window

      try:
          # Calculate moving average
          self.stock_data['MA'] = self.stock_data['Close'].rolling(window=window).mean()
          print(f"Moving average (window={window}) calculated successfully.")
      except Exception as e:
          print(f"Error calculating moving average: {e}")

    def visualize_moving_average(self, plot_start = None, plot_end = None):

      plot_start = plot_start or self.start_date
      plot_end = plot_end or self.end_date

      try:
        if plot_start < self.start_date:
          raise Exception("Date Error: Plot Start date provided is before the Data Fetch start date")
        elif plot_end > self.end_date:
          raise Exception("Date Error: Plot End date provided is after the Data Fetch end date")
        else:
          plot_data = self.stock_data[(self.stock_data['Date'] >= plot_start) & (self.stock_data['Date'] <= plot_end)]

          candlestick_trace = go.Candlestick(x=plot_data['Date'],
                                   open=plot_data['Open'],
                                   high=plot_data['High'],
                                   low=plot_data['Low'],
                                   close=plot_data['Close'],
                                   name='Value')
          ma_trace = go.Scatter(x=plot_data['Date'],
                                y=plot_data['MA'],
                                mode='lines',
                                name=f'Moving Average ({self.window}-day)',
                                line=dict(color="#0000ff"))

          layout = go.Layout(title='Candlestick Chart with Moving Average',
                            xaxis=dict(title='Date'),
                            yaxis=dict(title='Price'))

          fig = go.Figure(data=[candlestick_trace, ma_trace], layout=layout)
          fig.update_layout(xaxis_rangeslider_visible=False)

          fig.show()
      except Exception as e:
        print(e)

    def perform_macd(self, short_window=13, long_window=33, signal_window=9):
      try:
          # Calculate short-term and long-term exponential moving averages
          short_ema = self.stock_data['Close'].ewm(span=short_window, adjust=False).mean()
          long_ema = self.stock_data['Close'].ewm(span=long_window, adjust=False).mean()

          # Calculate MACD and signal line
          self.stock_data['MACD'] = short_ema - long_ema
          self.stock_data['Signal_Line'] = self.stock_data['MACD'].ewm(span=signal_window,\
                                                                       adjust=False).mean()

          print("MACD analysis performed successfully.")
      except Exception as e:
          print(f"Error performing MACD analysis: {e}")

    def visualize_macd(self, plot_start = None, plot_end = None):
      plot_start = plot_start or self.start_date
      plot_end = plot_end or self.end_date
      try:
        if plot_start < self.start_date:
          raise Exception("Date Error: Plot Start date provided is before the Data Fetch start date")
        elif plot_end > self.end_date:
          raise Exception("Date Error: Plot End date provided is after the Data Fetch end date")
        else:
          plot_data = self.stock_data[(self.stock_data['Date'] >= plot_start) & (self.stock_data['Date'] <= plot_end)]

          macd_trace = go.Scatter(x=plot_data['Date'], y=plot_data['MACD'], mode='lines', name='MACD')
          signal_trace = go.Scatter(x=plot_data['Date'], y=plot_data['Signal_Line'], mode='lines', name='Signal Line')

          layout = go.Layout(title='MACD Indicator',
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='MACD Value'))
          fig = go.Figure(data=[macd_trace, signal_trace], layout=layout)
          fig.show()
      except Exception as e:
        print(e)

    def visualize_macd_histogram(self, plot_start=None, plot_end=None):
      try:
          # Calculate MACD Histogram
          self.stock_data['MACD_Histogram'] = self.stock_data['MACD'] - self.stock_data['Signal_Line']

          # Visualize MACD Histogram
          plot_data = self.stock_data[(self.stock_data['Date'] >= plot_start) & (self.stock_data['Date'] <= plot_end)]
          histogram_trace = go.Bar(x=plot_data['Date'], y=plot_data['MACD_Histogram'], name='MACD Histogram')

          layout = go.Layout(title='MACD Histogram',
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='MACD Histogram'))

          fig = go.Figure(data=[histogram_trace], layout=layout)
          fig.show()

      except Exception as e:
          print(f"Error visualizing MACD Histogram: {e}")


    def calculate_bollinger_bands(self, window=20, num_std=2):
      try:
          # Calculate moving average
          self.stock_data['MA'] = self.stock_data['Close'].rolling(window=window).mean()

          # Calculate standard deviation
          self.stock_data['STD'] = self.stock_data['Close'].rolling(window=window).std()

          # Calculate upper and lower Bollinger Bands
          self.stock_data['Upper_Band'] = self.stock_data['MA'] + (num_std * self.stock_data['STD'])
          self.stock_data['Lower_Band'] = self.stock_data['MA'] - (num_std * self.stock_data['STD'])

          print(f"Bollinger Bands (window={window}, num_std={num_std}) calculated successfully.")
      except Exception as e:
          print(f"Error calculating Bollinger Bands: {e}")


    def visualize_bollinger_bands(self, plot_start=None, plot_end=None):
      plot_start = plot_start or self.start_date
      plot_end = plot_end or self.end_date
      try:
          if plot_start < self.start_date:
              raise Exception("Date Error: Plot Start date provided is before the Data Fetch start date")
          elif plot_end > self.end_date:
              raise Exception("Date Error: Plot End date provided is after the Data Fetch end date")
          else:
              plot_data = self.stock_data[(self.stock_data['Date'] >= plot_start) & (self.stock_data['Date'] <= plot_end)]
              candlestick_trace = go.Candlestick(x=plot_data['Date'],
                                                open=plot_data['Open'],
                                                high=plot_data['High'],
                                                low=plot_data['Low'],
                                                close=plot_data['Close'],
                                                name='Candlestick')
              upper_band_trace = go.Scatter(x=plot_data['Date'],
                                            y=plot_data['Upper_Band'],
                                            mode='lines',
                                            name='Upper Bollinger Band',
                                            line=dict(color="#FF5733"))
              lower_band_trace = go.Scatter(x=plot_data['Date'],
                                            y=plot_data['Lower_Band'],
                                            mode='lines',
                                            name='Lower Bollinger Band',
                                            line=dict(color="#33FF57"))
              layout = go.Layout(title='Bollinger Bands',
                                xaxis=dict(title='Date'),
                                yaxis=dict(title='Price'))

              fig = go.Figure(data=[candlestick_trace, upper_band_trace, lower_band_trace], layout=layout)
              fig.update_layout(xaxis_rangeslider_visible=False)
              fig.show()
      except Exception as e:
          print(e)


    def calculate_rsi(self, window=14):
      try:
          # Calculate daily price changes
          daily_changes = self.stock_data['Close'].diff()
          # Calculate average gains and losses over the specified window
          avg_gain = daily_changes.where(daily_changes > 0, 0).rolling(window=window).mean()
          avg_loss = -daily_changes.where(daily_changes < 0, 0).rolling(window=window).mean()
          # Calculate Relative Strength (RS)
          relative_strength = avg_gain / avg_loss
          # Calculate Relative Strength Index (RSI)
          self.stock_data['RSI'] = 100 - (100 / (1 + relative_strength))
          print(f"RSI (window={window}) calculated successfully.")
      except Exception as e:
          print(f"Error calculating RSI: {e}")

    def visualize_rsi(self, plot_start=None, plot_end=None):
      plot_start = plot_start or self.start_date
      plot_end = plot_end or self.end_date
      try:
          if plot_start < self.start_date:
              raise Exception("Date Error: Plot Start date provided is before the Data Fetch start date")
          elif plot_end > self.end_date:
              raise Exception("Date Error: Plot End date provided is after the Data Fetch end date")
          else:
              plot_data = self.stock_data[(self.stock_data['Date'] >= plot_start) & (self.stock_data['Date'] <= plot_end)]

              rsi_trace = go.Scatter(x=plot_data['Date'], y=plot_data['RSI'], mode='lines', name='RSI', line=dict(color="#FF5733"))

              # Add horizontal lines for overbought and oversold levels (e.g., 70 and 30)
              overbought_trace = go.Scatter(x=plot_data['Date'], y=[70] * len(plot_data), mode='lines', name='Overbought', line=dict(color="#FF0000"))
              oversold_trace = go.Scatter(x=plot_data['Date'], y=[30] * len(plot_data), mode='lines', name='Oversold', line=dict(color="#00FF00"))
              layout = go.Layout(title='Relative Strength Index (RSI)',
                                xaxis=dict(title='Date'),
                                yaxis=dict(title='RSI'))
              fig = go.Figure(data=[rsi_trace, overbought_trace, oversold_trace], layout=layout)
              fig.update_layout(xaxis_rangeslider_visible=False)
              fig.show()
      except Exception as e:
          print(e)

    def get_latest_news(self):
      try:
        if not self.ticker.news:
          raise Exception("No News: Cannot fetch latest news.")
        else:
          for news in self.ticker.news:
            print("Title: ", news['title'])
            print("Link: ", news['link'])
            print("Publisher: ", news['publisher'],"\n\n")
      except Exception as e:
        print(e)