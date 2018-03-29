#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 10:36:05 2018

@author: jonathan
"""

#preprocess return data
import pandas as p
import numpy as np
import sklearn.decomposition
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import usequity_functions as f
import importlib
importlib.reload(f)
from matplotlib import pyplot as plt

csv = 'all_stocks_5yr.csv'
index="date"
columns="Name"
values="close"

stocks_in = p.read_csv(csv)
stocks_in['date'] = p.to_datetime(stocks_in['date'])
stocks = f.reshape(stocks_in,index=index,columns=columns,values=values)
stocks_ret = f.get_ret(stocks) ## Rik in paper
stocks_ret = stocks_ret.iloc[1:len(stocks_ret)]
stocks = stocks.iloc[1:len(stocks)]

#for walkthrough
stocks = stocks.iloc[i:i+504]
stocks_ret = stocks_ret.iloc[i:i+504]
num_comps = 3



benchmark = p.read_csv("SP500.csv")
benchmark.index = benchmark['DATE']
benchmark = benchmark['SP500']
benchmark = p.DataFrame(benchmark)
joined = stocks_ret.join(benchmark,how='left')
joined['SP500'] = joined['SP500'].astype(float)
joined['Benchmark_ret'] = f.get_ret(joined['SP500'])
benchmark_ret = joined['Benchmark_ret'].iloc[1:len(joined)]

import statsmodels.formula.api as sm
#x is factor returns




bench = benchmark_ret[-60:]
Y = p.DataFrame(stocks_ret_std.iloc[-60:,1])
df = p.concat([Y,X],axis=1)
df.columns = ['Stock','Int','F1','F2','F3']
result = sm.ols(formula="Stock~ F1+F2+F3",data=df).fit()
result.summary()

result2 = sm.ols(formula="AAL~Benchmark_ret",data=df).fit()
result2.summary()

## i think my market factor could be off cause of equal weigted returns

def factor_rets (stocks_ret, num_comps):
    # need to complete standardization, cov, eig vals / vecs inside function b/c of 252 day window
    stocks_ret_std = StandardScaler().fit_transform(stocks_ret)
    stocks_ret_std = p.DataFrame(stocks_ret_std)
    stocks_ret_std.index = stocks_ret.index
    
    stocks_log = np.log(stocks)
    stocks_std = StandardScaler().fit_transform(stocks_ret)
    ### eigenvectors are returned standardized in numpy
    ## getting complex number when doing this with 252*470 b/c can't invert matrix
    ## need more granular data or extend window, will extend window to two years for now (504 days)
    #cov_mat = np.cov(stocks_ret_std.T)
    #eig_vals,eig_vecs = np.linalg.eig(cov_mat)
    
    ## same result using correlation matrix
    ## getting complex number when doing this with 252*470
    cov_mat = np.corrcoef(stocks_ret.T)
    eig_vals,eig_vecs = np.linalg.eig(cov_mat)
    
    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]
    
    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs.sort(key=lambda x: x[0], reverse=True)
    
    sigma_bar = stocks_ret.apply(np.std,axis=0)
    #SVD has sign issues, but good check
    #u,s,v = np.linalg.svd(stocks_ret_std.T)
    factor_returns = []
    for i in range(num_comps):
        V = eig_pairs[i][1]  #standardized eigenvector, numpy standardizes automatically
        eig_val = eig_pairs[i][0]
        portfolio_weights = (1/np.sqrt(eig_val)) * (V / sigma_bar) ## run standardized returns against this
        portfolio_weights1 = V                    ## non standardized rets, if i standardize after will it be the same?
        ## last row of stocks _ret, trailing 252 day window, local variable
        F = np.matmul(stocks_ret,portfolio_weights) 
        factor_returns.append(F)
        ## need to multiply by non standardized returns also,cause eigenvectors are standardized
   
    factor_returns = p.DataFrame(factor_returns).T
    factor_returns.index = stocks_ret.index
    
    
    intercept = p.Series(np.ones(len(factor_returns)),index=factor_returns.index)
    X = p.concat([intercept,factor_returns],axis =1 )
    X = X[-60:]
    # this function only needs to take in y because we are not iterating X
    def matrix_regression(y):
        b = np.matmul(np.matmul(np.linalg.inv(np.matmul(X.T,X)),X.T),y)
        e = y - np.matmul(X,b)
        return list(b) , list(e)
    
    betas = []
    residuals = []
    
    for j in range(len(stocks_ret.columns)):
        b = matrix_regression(stocks_ret_std.iloc[-60:,j])[0]
        e = matrix_regression(stocks_ret_std.iloc[-60:,j])[1]
        betas.append(b)
        residuals.append(e)
    
    
    out_betas = p.DataFrame(betas)
    out_resid = p.DataFrame(residuals)
    out_betas.index =  stocks_ret.columns
    out_betas.columns = ['Intercept','PC1','PC2','PC3']
    out_resid.index = stocks_ret.columns        
    
    def autoregression (y):
        y_tminus1 = y.shift(1)
        intercept = p.Series(np.ones(len(y)))
        y_tminus1 = p.concat([intercept,y_tminus1],axis =1)
        y_tminus1 = y_tminus1[1:len(y_tminus1)]
        y = y[1:len(y)]
        b = np.matmul(np.matmul(np.linalg.inv(np.matmul(y_tminus1.T,y_tminus1)),y_tminus1.T),y)
        e = y - np.matmul(y_tminus1,b)
        a = b[0]
        b = b[1:len(b)]
        return a,list(b),list(e)
    
    a = []
    b = []
    z = []
    
    for i in range(len(out_resid)):
        alpha = autoregression(out_resid.iloc[i,:])[0]
        beta = autoregression(out_resid.iloc[i,:])[1]
        zeta = autoregression(out_resid.iloc[i,:])[2]
        a.append(alpha)
        b.append(beta)
        z.append(zeta)
        
    a = p.DataFrame(a)  
    b = p.DataFrame(b)  
    z = p.DataFrame(z)
    a.index = b.index = z.index = out_betas.index
   
    z_var = z.apply(np.var,axis=1)
   
    part1 = (1-b)
    part2 = p.DataFrame(np.sqrt(z_var))
   
    denom = part1*part2
    numer = -a*np.sqrt(1-b**2)
    s = numer / denom

    return s












