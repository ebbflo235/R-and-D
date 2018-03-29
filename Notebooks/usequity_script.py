# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 16:38:51 2018

@author: Jonathan Schroeder
"""
## clear variables before starting

#%reset

import pandas as p
import numpy as np
import sklearn.decomposition
from sklearn.decomposition import PCA

##calls functions
import usequity_functions as f
import importlib
importlib.reload(f)

csv = 'all_stocks_5yr.csv'
index="date"
columns="Name"
values="close"

stocks_in = p.read_csv(csv)
stocks_in['date'] = p.to_datetime(stocks_in['date'])
stocks = f.reshape(stocks_in,index=index,columns=columns,values=values)
stocks_ret = f.get_ret(stocks) ## Rik in paper
stocks_ret = stocks_ret.iloc[1:len(stocks_ret)]
stocks_ret

R_bar = stocks_ret.apply(np.mean, axis = 0)
Sigma_bar = stocks_ret.apply(np.std, axis = 0)
#Sigma_bar = np.sqrt(Sigma_squared_bar)

def standardize (Rik):
    Yik = (Rik - R_bar)/Sigma_bar
    return Yik
    
## my scaler
Yik = stocks_ret.apply(standardize, axis = 1)
## see if it matches automatic scaler
from sklearn.preprocessing import StandardScaler
stocks_ret_std = StandardScaler().fit_transform(stocks_ret)
stocks_std = StandardScaler().fit_transform(stocks)

#extract factors using PCA
# transpose to get 470 by 470
cor_mat1 = np.corrcoef(stocks_ret_std.T)
eig_vals , eig_vecs = np.linalg.eig(cor_mat1)

print('Eigenvectors \n%s' %eig_vecs)
print('\nEigenvalues \n%s' %eig_vals)

cor_mat2 = np.corrcoef(Yik.T)
eig_vals1 , eig_vecs1 = np.linalg.eig(cor_mat2)
## looks like I am getting the same whether I am using my standardization or automatic, not sure what is different


## not sure what singular value decomposition is, but results should be same as eigenvectors and they are, good
u,s,v = np.linalg.svd(stocks_ret_std.T)

# Make a list of (eigenvalue, eigenvector) tuples
eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]

# Sort the (eigenvalue, eigenvector) tuples from high to low
eig_pairs.sort(key=lambda x: x[0], reverse=True)

# Visually confirm that the list is correctly sorted by decreasing eigenvalues
print('Eigenvalues in descending order:')
for i in eig_pairs:
    print(i[0])

########################################################################################################################
tot = sum(eig_vals)
var_exp = [(i / tot)*100 for i in sorted(eig_vals, reverse=True)]
var_exp = var_exp[0:20] ## took top 7
cum_var_exp = np.cumsum(var_exp)
from matplotlib import pyplot as plt
with plt.style.context('seaborn-whitegrid'):
    plt.figure(figsize=(8, 4))

    plt.bar(range(20), var_exp, alpha=0.5, align='center',
            label='individual explained variance')
    plt.step(range(20), cum_var_exp, where='mid',
             label='cumulative explained variance')
    plt.ylabel('Explained variance ratio')
    plt.xlabel('Principal components')
    plt.legend(loc='best')
    plt.tight_layout()
###########################################################################################################################

## choosing top 3 factors from PCA for eigenportfolio

Q = eig_vecs[:,0] / Sigma_bar
F = np.matmul(Q,stocks_ret.iloc[0])


stocks_ret_std = p.DataFrame(stocks_ret_std)
out  = stocks_ret_std.rolling(252,center = False).apply(roll)


##eigenvectors are horizontal
## maybe use to also calculate factor returns
def pca (stocks_matrix,time):
    pca = sklearn.decomposition.PCA(n_components = 3)
    pca.fit(stocks_ret_std)
    eigenvectors = pca.components_
    #eigenvalues = pca.explained_variance_ratio_
    Sigma_bar = stocks_ret.apply(np.std, axis = 0)
    factor_rets = []
    for i in range(len(eigenvectors)):
        Q = eigenvectors[i] / Sigma_bar
        F = np.matmul(Q,stocks_ret.iloc[time]) ## non standardized stocks ret, needs to stay same for each eigenvector loop
        factor_rets.append(F)
    return factor_rets

#def pca (stocks_matrix):
#    cor_mat = np.corrcoef(stocks_matrix.T)
#    eig_vals , eig_vecs = np.linalg.eig(cor_mat)
#    return tuple(eig_vals),tuple(eig_vecs.T)
## transponse eigenvecs before tuple to get correct vecs, i believe

empty_values = []
empty_vectors = []
for i in range(len(stocks_ret_std.index)-252):
    empty_values.append(pca(stocks_ret_std.iloc[i:i+252])[1])
    empty_vectors.append(pca(stocks_ret_std.iloc[i:i+252])[0])

## the last row is the most recent    
        
empty_values = p.core.frame.DataFrame(empty_values)
empty_vectors = p.core.frame.DataFrame(empty_vectors)

start = np.zeros((20,2))
eigenvalues = np.concatenate((start,empty),axis=0)
eigenvalues = p.core.frame.DataFrame(eigenvalues)
stocks[['E1','E2']] = empty.iloc[:,0:2]
