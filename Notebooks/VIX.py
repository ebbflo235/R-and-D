# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 10:03:34 2018

@author: Jonathan Schroeder
"""
#import time series features
import statsmodels.api as sm
from statsmodels.tsa import stattools as st
from statsmodels.tsa import ar_model as ar
from statsmodels.tsa import arima_model as arma
from statsmodels.tsa.vector_ar import var_model as var
import seaborn as sea

#general operating features including self created functions
import pandas as p
import numpy as np
import functions as s
import importlib
importlib.reload(s)

#read data
csv = "vixcurrent.csv"
vix = p.read_csv(csv,index_col = 0)
vix = vix[vix.VIX != 0]

## 10 year has some missing data.... lets focus on vix and sp500
#vix = vix[vix['10yr'] != "."]

vix = vix.iloc[:,0:2]
vix = vix.astype(float)
##

vix['SP500_ret'] = s.get_ret(vix['SP500'])
vix['Delta_VIX'] = vix['VIX'] - vix['VIX'].shift(1)
vix['Delta_VIX_lag'] = vix['Delta_VIX'].shift(1)

#################################################################
vix['252_Day_ret'] = vix['SP500']/vix['SP500'].shift(252)-1
vix['21day_Delta_VIX'] = vix['VIX'] - vix['VIX'].shift(21)
##incorporate SD of Delta vix as well?
vix['Delta_vix_t-252'] = vix['Delta_VIX'].shift(252)
vix['21day_Delta_vix_t-252'] = vix['21day_Delta_VIX'].shift(252)

to_label = list(range(1,51))
vix['Rolling_2'] = p.rolling_apply(vix['21day_Delta_vix_t-252'],252,lambda x: p.qcut(x,50,labels=to_label)[49])

## work on changing this.. make function that takes in series and uses qcut to spit out groups.. shouldn't be that bad
vix['Rolling_3'] = vix['21day_Delta_vix_t-252'].rolling(window=252,center=False).apply(func=p.qcut(vix['21day_Delta_vix_t-252'],50,labels=to_label))

top1percent = vix.loc[vix['Rolling_2']==50]
bottom1percent = vix.loc[vix['Rolling_2']==1]


vix['Percentile'] = p.qcut(vix['Delta_vix_t-60'],100, labels = to_label)
vix['4Day_Percentile'] = p.qcut(vix['4day_Delta_vix_t-60'],100, labels = to_label)



top1percent = vix.loc[vix['4Day_Percentile']==100]
bottom1percent = vix.loc[vix['4Day_Percentile']==1]
#sea.regplot(top1percent['Percentile'],top1percent['60_Day_ret'])

#vix_lag60 = vix.iloc[60:len(vix)]

sea.regplot(vix_lag60['Delta_vix_t-60'],vix_lag60['60_Day_ret'])


vix = vix.iloc[2:len(vix)]

## Strong negative relationship between VIX and S&P
Y = vix['SP500_ret']
X = vix['Delta_VIX']
X = sm.add_constant(X)
ols_model = sm.OLS(Y,X)
results = ols_model.fit()
results.summary()
sea.regplot(X,Y)
sea.residplot(X,Y)
## 
X_lagged = vix['Delta_VIX_lag']
X_lagged = sm.add_constant(X_lagged)
ols_model = sm.OLS(Y,X_lagged)
results = ols_model.fit()
results.summary()
sea.regplot(X_lagged,Y)
sea.residplot(X_lagged,Y)

##look for autocorrelation - looks like some autocorrelation
st.pacf(X,nlags=3)
st.acf(X,nlags=3)
st.acf(Y,nlags=1)

##check for stationarity - appear stationary
st.adfuller(X)
st.adfuller(Y)

##vector autoregression
var_xy = vix[['SP500_ret','Delta_VIX']]
var_xy.index = p.to_datetime(var_xy.index)
var_model = var.VAR(var_xy)
var_res = var_model.fit()
var_res.summary()


csv_v = "vegas.csv"
vegas = p.read_csv(csv_v,index_col=0)
vegas = vegas.iloc[0:len(vegas)-2,:]
vegas = vegas.astype(float)

merged = vix.merge(vegas,left_index=True,right_index=True)
merged['SP500_ret'] = s.get_ret(merged['SP500'])
merged['LVS_ret'] = s.get_ret(merged['LVS'])
merged['MGM_ret'] = s.get_ret(merged['MGM'])
merged['MLCO_ret'] = s.get_ret(merged['MLCO'])
merged['Delta_VIX'] = merged['VIX'] - merged['VIX'].shift(1)
merged['Delta_VIX_lag'] = merged['Delta_VIX'].shift(1)

merged = merged.iloc[1:len(merged)]
Y = merged['SP500_ret']
Y = merged['MGM_ret']
X = merged['Delta_VIX_lag']

X_lvs = merged['LVS_ret']
X_mgm = merged['MGM_ret']
X_mlco = merged['MLCO_ret']

sea.regplot(X_lvs,Y)
sea.residplot(X_lvs,Y)

sea.regplot(X_mgm,Y)
sea.residplot(X_mgm,Y)

sea.regplot(X_mlco,Y)
sea.residplot(X_mlco,Y)


model_lvs = sm.OLS(X_mlco,Y)
res_lvs = model_lvs.fit()
res_lvs.summary()

sea.regplot(X,Y)
sea.residplot(Y,X_lvs)





