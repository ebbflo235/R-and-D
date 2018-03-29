# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 15:30:48 2018

@author: Jonathan Schroeder
"""
import os
os.chdir('C:\\Users\\Jonathan Schroeder\Desktop\Volatility Timing')

## clear variables before starting

#%reset

## Fade big moves, go with small moves, do nothing in the middle

import pandas as p
import numpy as np
import matplotlib.pyplot as plt

##bid ask tick level data
csv = "Tick_data_EURUSD.csv"
eur_ba = p.read_csv(csv)
eur_ba.columns = ['Local Time','Ask','Bid','Ask Volume','Bid Volume']
eur_ba['Local Time'] = p.to_datetime(eur_ba['Local Time'])

## subtracting time
GMT_eur = eur_ba
GMT_eur['Local Time'] = eur_ba['Local Time'] - p.DateOffset(hours=8)
GMT_eur.columns = ['GMT Time','Ask','Bid','Ask Volume','Bid Volume']

GMT_eur['Year'] = p.DatetimeIndex(GMT_eur["GMT Time"]).year
GMT_eur['Month'] = p.DatetimeIndex(GMT_eur["GMT Time"]).month
GMT_eur['Day'] = p.DatetimeIndex(GMT_eur["GMT Time"]).day
GMT_eur['Hour'] = p.DatetimeIndex(GMT_eur["GMT Time"]).hour
###### add in times shorter than an hour ############################################################################
GMT_eur['Minute'] = p.DatetimeIndex(GMT_eur["GMT Time"]).minute

       
       
######################################################################################################################       
GMT_eur['Price'] = (GMT_eur['Bid'] + GMT_eur['Ask']) / 2
       
def total_return(prices):
    """Retuns the return between the first and last value of the DataFrame.
    Parameters
    ----------
    prices : pandas.Series or pandas.DataFrame
    Returns
    -------
    total_return : float or pandas.Series
        Depending on the input passed returns a float or a pandas.Series.
    """
    return prices.iloc[-1] / prices.iloc[0] - 1       

       
GMT_daily_ret = GMT_eur.groupby(['Year', 'Month','Day','Hour','Minute'])['Price'].apply(total_return)     
GMT_daily_volume = GMT_eur.groupby(['Year', 'Month','Day','Hour','Minute'])['Ask Volume','Bid Volume'].sum()        
GMT_daily_volume['Volume Diff'] = GMT_daily_volume['Bid Volume'] - GMT_daily_volume['Ask Volume']    
GMT_daily_volume['Total Volume'] = abs(GMT_daily_volume['Bid Volume']) + abs(GMT_daily_volume['Ask Volume'] )  

eur_volume = GMT_daily_volume.join(GMT_daily_ret)
eur_volume.columns = ['Ask Volume','Bid Volume','Volume Diff','Total Volume','Return']

#########################################################################################################################
## lets look at more extreme values by dividing into quintiles
eur_volume['Quintile'] = p.qcut(eur_volume['Volume Diff'],5, labels = [1,2,3,4,5])

## lets fade big movers and go with small
#eur_volume['Trade'] = np.where((eur_volume['Quintile'] == 2) | (eur_volume['Quintile'] == 5), 'Sell' , np.where((eur_volume['Quintile'] == 1) | (eur_volume['Quintile'] == 4), 'Buy', 'No trade' ))
eur_volume['Trade'] = np.where(eur_volume['Quintile'] == 1, 'Sell' , np.where(eur_volume['Quintile'] == 5 , 'Buy', 'No trade' ))
eur_volume['Trade_lag'] = eur_volume['Trade'].shift(1)
eur_volume['Result'] = np.where(eur_volume['Trade_lag'] == 'Sell', -1*eur_volume['Return'], np.where(eur_volume['Trade_lag'] == 'Buy', eur_volume['Return'],0) )
eur_volume['$100 a day QUINTILE'] = eur_volume['Result']*100
eur_volume['$100 a day QUINTILE'].sum()

def quintile(series):
    return p.qcut(series,5,labels=[1,2,3,4,5])

eur_volume['Rolling Quintile'] = eur_volume['Volume Diff'].rolling(20).max()

eur_volume = GMT_eur.groupby(['Year', 'Month'])['Volume Diff'].apply(quintile)   
GMT_daily_volume['Year'] = p.DatetimeIndex(eur_volume["GMT Time"]).year
GMT_daily_volume['Month'] = p.DatetimeIndex(eur_volume["GMT Time"]).month
###############################################################################################################################
#### This is the one that has theoretical merit but you need to get different trade data as what you are using right now is bid ask volume
#### when you really want trades that crossed the spread to measure directional volume
eur_volume['Rolling_quintile'] = p.rolling_apply(eur_volume['Total Volume'],60,lambda x: p.qcut(x,5,labels=[1,2,3,4,5])[59])
eur_volume['Trade_rolling'] = np.where(eur_volume['Rolling_quintile'] == 5, 'Sell' , np.where(eur_volume['Rolling_quintile'] == 1 , 'Buy', 'No trade' ))
eur_volume['Trade_rolling_lag'] = eur_volume['Trade_rolling'].shift(1)
eur_volume['Result_rolling'] = np.where(eur_volume['Trade_rolling_lag'] == 'Sell', -1*eur_volume['Return'], np.where(eur_volume['Trade_rolling_lag'] == 'Buy', eur_volume['Return'],0) )
eur_volume['$100_rolling'] = eur_volume['Result_rolling']*100
eur_volume['$100_rolling'].sum()
