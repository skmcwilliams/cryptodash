#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 09:21:48 2021

@author: skm
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import cbpro

class Coin:
    """coin class"""
    def __init__(self):
        pass
    
    def get_data(self,symbol,granularity):
        """pull data from required symbols using the historic rates function
        of cbpr/coinbase."""
        public_client = cbpro.PublicClient() #instantiate client
        hist = public_client.get_product_historic_rates(f'{symbol}', granularity=granularity) # get data
        df = pd.DataFrame(hist) # convert data into df
        df = df.rename(columns={0:'time',1:'low',2:'high',3:'open',4:'close',5:'volume'}) #rename cols according to docs
        df['time']=pd.to_datetime(df['time'], unit='s') #convert to time using seconds
        return df
        
class BTC(Coin):
    """class of Bitcoin, inherits Coin class"""
    def __init__(self):
        pass
    
    
    def plot(self):
        """plot data using plotly"""
        df = Coin.get_data(self,'BTC-USD',86400) #pull bitcoin trading data at hourly intervals
        df['vwap'] = np.cumsum(df['volume']*(df['high']+df['low']+df['close'])/3) / np.cumsum(df['volume']) #add vwap col
        df['$_change'] = df['close'] - df['open'] # create change col
        
        fig = make_subplots(specs=[[{"secondary_y": True}]]) # creates ability to plot vol and $ change within main plot

        # include OHLC (already comes with rangeselector)
        fig.add_trace(go.Ohlc(x=df['time'],
                        open=df['open'], 
                        high=df['high'],
                        low=df['low'], 
                        close=df['close'],name='Bar'))
        
        # include a go.Bar trace for volume
        fig.add_trace(go.Bar(x=df['time'], y=df['volume'],name='Volume'),
                       secondary_y=False)
        
        # include go.Scatter for VWAP line
        fig.add_trace(go.Scatter(x=df['time'],y=df['vwap'],name='VWAP'))
        fig.add_trace(go.Bar(x=df['time'],y=df['$_change'],name='$ Change'))
        fig.layout.yaxis2.showgrid=False
        fig.update_layout(title_text='BTC-USD')
        return fig


class ETH(Coin):
    """class of Ethereum"""
    def __init__(self):
        pass
    
    
    def plot(self):
        eth_df = Coin.get_data(self,'ETH-BTC',60) #pull BTC-USD data by the minute
        btc_df = Coin.get_data(self,'BTC-USD',60) #pull ETH-BTC data by the minute
        df = pd.merge(eth_df,btc_df,on='time',how='left') #merge into dataframe
        
        #conduct volume calc in USD by taking average price of ETH-BTC, multiplying by volume, then multiplying by average BTC-USD price
        df['usd_vol'] = ((df['high_x']+df['low_x']+df['close_y'])/3)*df['volume_x']*((df['high_y']+df['low_y']+df['close_y'])/3)
         
        fig = go.Figure([go.Bar(x=df['time'], y=df['usd_vol'])])
        
        # update with title and rangeslider
        fig.update_layout(title_text='ETH-BTC Volume',
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        return fig
 
# stock language needed for Plotly Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

#instantiate BTC and ETH, call plot functions
btc = BTC()
btc_fig = btc.plot()
eth = ETH()
eth_fig = eth.plot()

# Dash app language
app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children="SKM's Cryptoboard"),

        html.Div(children='''
            Live data provided via Coinbase using the coinbase-pro API: https://github.com/danpaquin/coinbasepro-python
        '''),

        dcc.Graph(id='BTC/USD',figure=btc_fig), #build chart and set size default
        dcc.Markdown('''
                The above chart shows is a OHLC bar chart for each hour, along with volume, change (in USD),
                and VWAP
                ''')   
    ]),

    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children=''),

        dcc.Graph(id='ETH/BTC',figure=eth_fig), # build chart and set size default
        dcc.Markdown('''
                The above chart shows ETH-BTC volume converted to USD on a per minute basis
                ''') 
    ]),
])

if __name__=='__main__':
    app.run_server(debug=True)   
            
        

