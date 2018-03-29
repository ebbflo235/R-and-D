# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 16:14:37 2017

@author: Jonathan Schroeder
"""
 
def reshape(data,index,columns,values,**output):
    reshaped = data.pivot_table(index=index,columns=columns,values=values)
    if (output == "NA"):
        return reshaped 
    else:
        nona = reshaped.dropna(axis=1,how='any')
        return nona

def get_ret (data):
    return data/data.shift(1)-1

def returns(data):
    returns = data.apply(get_ret,axis=0)
    returns = returns.iloc[1:len(returns),:]
    return returns 
    
def shrinkage_input(data):
    
    t = data.shape[0]
    n = data.shape[1]

    import numpy as np
    sample_var = data.apply(np.var,axis=0)
    sample_mean = data.apply(np.mean,axis=0)
    grand_mean = np.mean(sample_mean)
    sigma = ((1/t)*sample_var)
    omega_sq = (1/n)*np.sum(sigma)
    demeaned = (sample_mean - grand_mean)**2
    delta_sq = (1/n)*np.sum(demeaned)
    beta = delta_sq/(omega_sq+delta_sq)
    
    return beta, sample_var, sample_mean, grand_mean
    
def mean_est (beta, grand_mean, sample_mean):
    mean_est = (1-beta)*grand_mean+beta*sample_mean
    return mean_est

##
def sample_cov (data):
    import numpy as np
    out_cov = np.cov(data,rowvar = False)
    return out_cov

def daily_cov_dist (mat1,mat2,i):
    import numpy as np
    Xt = mat1.iloc[i,:]
    XtXt = np.outer(Xt,Xt)   
    dist = (XtXt - mat2)**2
    out = np.apply_along_axis(np.sum,0,dist)
    return np.sum(out)

"""
def shrink_cov(data,i):
    
    import numpy as np
    t = data.shape[0]
    n = data.shape[1]

    variances = (1/t)*shrinkage_input(data)[1]
    sigma_bar = (1/n)*np.sum(np.sqrt(variances))
    a= np.zeros((n,n),float)
    sig_bar_ident = np.fill_diagonal(a,sigma_bar)
    
    Xt = data.iloc[i,:]
    XtXt = np.outer(Xt,Xt) 
    S = (1/t)*np.sum(XtXt)    
    
    omega_sq = 1/(t*(t-1))* 
"""








