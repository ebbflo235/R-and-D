# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order

def make_contract(symbol, sec_type, exch, prim_exch, curr):
    Contract.m_symbol = symbol
    Contract.m_secType = sec_type
    Contract.m_exchange = exch
    Contract.m_primaryExch = prim_exch
    Contract.m_currency = curr
    return Contract
    
def make_order(action, quantity, price = None ):
    if price is not None:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        order.m_lmtPrice
    
    else:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        
    return order

def main():
    conn = Connection.create(port=7496, clientId = 999)
    conn.connect()
    oid = 13
    cont = make_contract('AAPL','STK','SMART','SMART','USD')
    offer = make_order('BUY',1,50)
    conn.placeOrder(oid,cont,offer)
    conn.disconnect()
    
main()

CheckConnection()
