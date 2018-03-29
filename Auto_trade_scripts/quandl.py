# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import quandl 
import numpy as np
import pandas as p
from scipy import stats

quandl.ApiConfig.api_key = *****
all_data = quandl.get_table('SHARADAR/SF1',qopts={"Columns":["ticker","dimension","calendardate","datekey","reportperiod","lastupdated","GROSSMARGIN","INVENTORY","NCF","ASSETSC","CASHNEQUSD","LIABILITIESC","DEBTC","TAXLIABILITIES","DEPAMOR"]},dimension = 'ARQ',paginate=True)
sample = all_data.iloc[0:1000,:]


def get_tickers ():
   all_stocks = quandl.get_table('SHARADAR/SF1',qopts={"Columns":["ticker","dimension","calendardate","datekey","reportperiod","lastupdated","GROSSMARGIN","INVENTORY","NCF","ASSETSC","CASHNEQUSD","LIABILITIESC","DEBTC","TAXLIABILITIES","DEPAMOR"]},dimension = 'ARQ',calendardate='2013-09-30',paginate=True)
   all_stocks = all_stocks.dropna()
   tickers = p.DataFrame(all_stocks['ticker'].unique())
   
   all_int = quandl.get_table('SHARADAR/SF3A', qopts = {"Columns":["ticker","calendardate","shrvalue","cllvalue","putvalue"]},calendardate = '2013-09-30',paginate = True)
   all_int = all_int[(all_int != 0).all(1)]
   tickers_int = p.DataFrame(all_int['ticker'].unique())
   tickers_to_use = p.Series(np.intersect1d(tickers,tickers_int))
   return tickers_to_use

tickers = get_tickers()

## should I make accruals and ncf one score?
def get_fundamentals(ticker):
    
    stock_fundamentals = quandl.get_table('SHARADAR/SF1',qopts={"Columns":["ticker","dimension","calendardate","datekey","reportperiod","lastupdated","GROSSMARGIN","INVENTORY","NETINC","ASSETSC","CASHNEQUSD","LIABILITIESC","DEBTC","TAXLIABILITIES","DEPAMOR"]},dimension = 'ARQ',ticker=ticker,paginate=True)
    
    #apple['accruals'] = (apple['assetsc'] - apple['cashnequsd']) - (apple['liabilitiesc']-apple['debtc']-apple['taxliabilities']) - apple['depamor']
    
    stock_fundamentals['delta_margin'] = stock_fundamentals['grossmargin'] - stock_fundamentals['grossmargin'].shift(1)
    stock_fundamentals['delta_inventory'] = stock_fundamentals['inventory'] - stock_fundamentals['inventory'].shift(1)
    stock_fundamentals['delta_netinc'] = stock_fundamentals['netinc'] - stock_fundamentals['netinc'].shift(1)
    stock_fundamentals['delta_assetsc'] = stock_fundamentals['assetsc'] - stock_fundamentals['assetsc'].shift(1)
    stock_fundamentals['delta_cashnequsd'] = stock_fundamentals['cashnequsd'] - stock_fundamentals['cashnequsd'].shift(1)
    stock_fundamentals['delta_liabilitiesc'] = stock_fundamentals['liabilitiesc'] - stock_fundamentals['liabilitiesc'].shift(1)
    stock_fundamentals['delta_debtc'] = stock_fundamentals['debtc'] - stock_fundamentals['debtc'].shift(1)
    stock_fundamentals['delta_taxliabilities'] = stock_fundamentals['taxliabilities'] - stock_fundamentals['taxliabilities'].shift(1)
    stock_fundamentals['delta_depamor'] = stock_fundamentals['depamor'] - stock_fundamentals['depamor'].shift(1)
    stock_fundamentals['delta_accruals'] = (stock_fundamentals['delta_assetsc'] - stock_fundamentals['delta_cashnequsd']) - (stock_fundamentals['delta_liabilitiesc']-stock_fundamentals['delta_debtc']-stock_fundamentals['delta_taxliabilities']) - stock_fundamentals['delta_depamor']
    stock_fundamentals['delta_cash_comp'] = stock_fundamentals['delta_netinc'] - stock_fundamentals['delta_accruals']
    
    #margin transform
    stock_fundamentals.loc[stock_fundamentals['delta_margin'] >= 0, 'margin_score'] = 1
    stock_fundamentals.loc[stock_fundamentals['delta_margin'] < 0, 'margin_score'] = 0
    
    #accrual transform --> positive change is bad, thus denoting it with zero
    stock_fundamentals.loc[stock_fundamentals['delta_accruals'] >= 0, 'accruals_score'] = 0
    stock_fundamentals.loc[stock_fundamentals['delta_accruals'] < 0, 'accruals_score'] = 1
    
    #net cash flow --> indicator is premade, may want to creat own but looks okay for now
    stock_fundamentals.loc[stock_fundamentals['delta_cash_comp'] >= 0, 'cash_comp_score'] = 1
    stock_fundamentals.loc[stock_fundamentals['delta_cash_comp'] < 0, 'cash_comp_score'] = 0
    
    #maybe add inventory later
    stock_fundamentals['fundamental_score'] = stock_fundamentals['margin_score'] + stock_fundamentals['accruals_score'] + stock_fundamentals['cash_comp_score']
    stock_fundamentals = stock_fundamentals.iloc[1:len(stock_fundamentals),:]

    return stock_fundamentals

fundamentals = get_fundamentals('SCS')

time_delta = p.Timestamp.today() - fundamentals['datekey'][fundamentals.index[-1]]
time_delta.days


tickers = p.DataFrame(all_data['ticker'].unique())

ticker = 'AAPL'

## look at taking debt into consideration? --> is this already taken into consideration by fundamentals? if so, what is better to use?
## look at taking total options value as indicator of volatility --> hard to make inferences from spread.
## use price for share value purchases to decide where to put limit orders
def get_institutional(ticker):

    stock_institutional = quandl.get_table('SHARADAR/SF3A', qopts = {"Columns":["ticker","calendardate","shrvalue","cllvalue","putvalue"]},ticker=ticker,paginate = True)
    stock_institutional["total_option_value"] = stock_institutional['cllvalue'] + stock_institutional['putvalue']
    stock_institutional = stock_institutional.sort_values(by=['calendardate'])
    stock_institutional["delta_option_value"] = stock_institutional["total_option_value"] - stock_institutional["total_option_value"].shift(1)
    stock_institutional["delta_shrvalue"] = stock_institutional["shrvalue"] - stock_institutional["shrvalue"].shift(1)
    stock_institutional = stock_institutional.iloc[1:len(stock_institutional),:]
    
    stock_institutional.loc[stock_institutional['delta_option_value'] >= 0, 'option_score'] = 1
    stock_institutional.loc[stock_institutional['delta_option_value'] < 0, 'option_score'] = 0
    
    stock_institutional.loc[stock_institutional['delta_shrvalue'] >= 0, 'share_value_score'] = 1
    stock_institutional.loc[stock_institutional['delta_shrvalue'] < 0, 'share_value_score'] = 0
    
    #stock_institutional['institutional_score'] = stock_institutional['share_value_score'] + stock_institutional['option_score']
    
    institutional_prices = []
    
    for date in stock_institutional['calendardate']:
        table = quandl.get_table('SHARADAR/SF3', calendardate=date, ticker=ticker)
        sticky_price = stats.mode(table['price'])[0]
        institutional_prices.append(sticky_price)
    out = p.DataFrame(institutional_prices)
    out.columns = ['stickyprice']
    out.index = stock_institutional.index
    out_merge = stock_institutional.join(out)

    return out_merge



institutional = get_institutional('SCS')


apple_institutional['calendardate'] = p.to_datetime(apple_institutional['calendardate'])
## get return data for event study and to run some regressions to test


total = apple_fundamentals.merge(apple_institutional,on='calendardate',how='left')


apple_prices = quandl.get_table('SHARADAR/SEP', ticker='GS')

### stand alone function or embedded?
def sticky_prices (ticker):
    institutional_prices = []
    for date in stock_institutional['calendardate']:
        table = quandl.get_table('SHARADAR/SF3', calendardate=date, ticker=ticker)
        sticky_price = stats.mode(table['price'])[0]
        institutional_prices.append(sticky_price)
    out = p.DataFrame(institutional_prices)
    out.columns = ['stickyprice']
    out.index = stock_institutional.index
    out_merge = stock_institutional.join(out)
    return institutional_prices





