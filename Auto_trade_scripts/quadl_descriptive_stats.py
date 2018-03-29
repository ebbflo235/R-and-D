#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 21:29:53 2018

@author: jonathan
"""
import statsmodels.api as sm
import seaborn as sea


def get_ret (data):
    return data/data.shift(1)-1    


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
    stock_fundamentals['fundamental_score'] = stock_fundamentals['margin_score']+stock_fundamentals['accruals_score'] + stock_fundamentals['cash_comp_score']
    
    stock_fundamentals = stock_fundamentals.iloc[1:len(stock_fundamentals),:]

    return stock_fundamentals

fundamentals = get_fundamentals('PEG')


## test with day after prices
## test with not just accruals, but with institutional buying
## find a way to test with much more than just apple and see if combining works better in those situations
apple_prices = p.DataFrame(  quandl.get_table('SHARADAR/SEP', ticker='PEG'))
fundamentals.loc[fundamentals['fundamental_score'] < 3, 'fundamental_score'] = 0
fundamentals.loc[fundamentals['fundamental_score'] == 3, 'fundamental_score'] = 1
out = fundamentals.merge(apple_prices, left_on = 'datekey',right_on='date',how='left')
out['ret_close'] = get_ret(out['close'])
out = out.iloc[1:len(out),:]
out['ret_lag'] = out['ret_close'].shift(-1)
out = out.iloc[0:len(out)-1,:]

Y = out['ret_lag']
X = out['fundamental_score']
X = sm.add_constant(X)
ols_model = sm.OLS(Y,X)
results = ols_model.fit()
results.summary()

