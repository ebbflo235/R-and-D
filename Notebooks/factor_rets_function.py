#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 17:40:36 2018

@author: jonathan
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:48:55 2018

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
#stocks_ret = stocks_ret.iloc[:,0:5]

##############################################################################
benchmark = p.read_csv("SP500.csv")
benchmark.index = benchmark['DATE']
benchmark = benchmark['SP500']
benchmark = p.DataFrame(benchmark)
joined = stocks_ret.join(benchmark,how='left')
joined['SP500'] = joined['SP500'].astype(float)
joined['Benchmark_ret'] = f.get_ret(joined['SP500'])
benchmark_ret = joined['Benchmark_ret'].iloc[1:len(joined)]
##############################################################################

#stocks_ret.to_csv('outR.csv')
#stocks_ret.to_csv('outR_std.csv')

def factor_rets (stocks_ret, num_comps):
    # need to complete standardization, cov, eig vals / vecs inside function b/c of 252 day window
    stocks_ret_std = StandardScaler().fit_transform(stocks_ret)
    ### eigenvectors are returned standardized in numpy
    ## getting complex number when doing this with 252*470 b/c can't invert matrix
    ## need more granular data or extend window, will extend window to two years for now (504 days)
    cov_mat = np.cov(stocks_ret_std.T)
    eig_vals,eig_vecs = np.linalg.eig(cov_mat)
    
    ## same result using correlation matrix
    ## getting complex number when doing this with 252*470
    #cor_mat = np.corrcoef(stocks_ret_std.T)
    #eig_vals,eig_vecs = np.linalg.eig(cor_mat)
    
    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]
    
    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs.sort(key=lambda x: x[0], reverse=True)
    
    #SVD has sign issues, but good check
    #u,s,v = np.linalg.svd(stocks_ret_std.T)
    factor_returns = []
    for i in range(num_comps):
        Q = eig_pairs[i][1] #standardized eigenvector, numpy standardizes automatically
        eig_val = eig_pairs[i][0]
        portfolio_weights = (1/np.sqrt(eig_val))*Q
        ## last row of stocks _ret, trailing 252 day window, local variable
        F = np.matmul(stocks_ret,portfolio_weights) 
        ## need to multiply by non standardized returns also,cause eigenvectors are standardized
        factor_returns.append(F)
    return tuple(factor_returns) # tuple is easier to see in variable explorer but little difference

eigen_ports = []
# if you manually walk through, make sure you reset because stocks_ret shrinks each time you run
for i in range(len(stocks_ret.index)-504):
    eigen_ports.append(factor_rets(stocks_ret.iloc[i:i+504],3))

#for walk through
#stocks_ret = stocks_ret.iloc[i:i+504]

df_factor_rets = p.DataFrame(eigen_ports)
df_factor_rets = df_factor_rets.astype(float)
intercept = p.DataFrame(np.ones(len(df_factor_rets)))
df_factor_rets = p.concat([intercept,df_factor_rets],axis=1)
#subsetting returns from X to match days where we have factor returns since we used 2 year rolling window, can 
#change for different datasets
Y_sub = stocks_ret.iloc[-len(df_factor_rets):]

#dont think it is used, can delete later:
    #df_factor_rets.index = Y_sub.index
    #combined = p.concat([Y_sub,df_factor_rets], axis = 1)

## matrix algebra for regression is working much faster than a package
def get_residuals(y,X):
    b = np.matmul(np.matmul(np.linalg.inv(np.matmul(X.T,X)),X.T),y)
    e = y - np.matmul(X,b)
    return b , e # does it need to be tuple, think it will just return list this way

residuals_matrix = []
beta_matrix = []

for i in range(len(Y_sub)-60):
    for j in range(len(Y_sub.columns)):
        residuals_matrix.append(get_residuals(y = Y_sub.iloc[i:i+60,j], X = df_factor_rets.iloc[i:i+60])[1])
        beta_matrix.append(get_residuals(y = Y_sub.iloc[i:i+60,j], X = df_factor_rets.iloc[i:i+60])[0])
## no residuals for first 60, so matrix will be 694*470 or (len(Y_sub)-60) * N

## use a generator to access lists of list
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]  

generator_resid = chunks(residuals_matrix,470)
generator_beta = chunks(beta_matrix,470)
      
# now I want to estimate 1 lag regression model for each residual
# should be easy to turn into function by iterating zero, but for now lets keep using the first stock until process is done
stock1_resid = []
stock1_beta = []
while True:
    try:
        stock1_resid.append(next(generator_resid)[3])
        stock1_beta.append(next(generator_beta)[3])
    except StopIteration:
        break

## when you look at this tomorrow, you may be one date short... not big deal but may want to include
resid_t0 = p.DataFrame(stock1_resid[0])
intercept2 = p.DataFrame(np.ones(len(resid_t0)))
intercept2.index = resid_t0.index
resid_t0 = p.concat([resid_t0,intercept2],axis=1)
resid_t0.columns = ['t+1','Intercept'] 
resid_t0['t'] = resid_t0['t+1'].shift(1)
resid_t0 = resid_t0[1:len(resid_t0)]

resid_of_resid = get_residuals(y = resid_t0['t+1'], X = resid_t0[['Intercept','t']])[1]
betas_of_resid = get_residuals(y = resid_t0['t+1'], X = resid_t0[['Intercept','t']])[0]
plt.plot(resid_of_resid)

















### have been using code below to test #####################################################################
out = p.DataFrame(eigen_ports)
out = out.astype(float)
out1 = out*-1

## same residual result regardless of sign of eigenvector
import statsmodels.formula.api as sm
X = benchmark_ret[-755:]
X1 = p.DataFrame(df_factor_rets[-755:])
Y = Y_sub.iloc[:,0]

#X1 = df_factor_rets.iloc[:,0:2]
#Y = Y_sub.iloc[:,356]
X1.index=Y.index
df = p.concat([Y,X],axis=1)
df.columns = ['A','Benchmark_ret']
result = sm.ols(formula="A~ Benchmark_ret",data=df).fit()
result.summary()
resid = result.resid
resid = p.DataFrame(resid)
## same residual result regardless of sign of eigenvector
X1 = out1[-60:]
Y1 = stocks_ret['GS'][-60:]
X1.index=Y1.index
df1 = p.concat([Y1,X1],axis=1)
df1.columns = ['Stock','F1','F2','F3']
result1 = sm.ols(formula="Stock~F1+F2+F3",data=df1).fit()
result1.summary()
resid1 = result1.resid
resid1 = p.DataFrame(resid1)

resid['t'] = resid.iloc[:,0].shift(-1)
resid.columns = ['t+1','t']
resid = resid[1:len(resid)]
y = resid['t+1']
x = resid['t']
res = sm.ols(formula="y~x",data=resid).fit()
res.summary()
res.params

