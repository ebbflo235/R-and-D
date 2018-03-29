#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 21:14:23 2018

@author: jonathan
"""

order_type = 'LMT'
action = 'BUY'
stock = 'GS'
quantity = 19
price = 262.35

def submit_order(ordertype,direction,orderid,stock,quantity):
    #ordertype = limit or market
    #direction = buy or sell
    #order id = unique identifier
    #stock = ticker
    #quantity = number of shares
    
    from ib.ext.Contract import Contract
    from ib.ext.Order import Order
    from ib.opt import Connection
    
    def error_handler(msg):
        print ("Server Error:", msg)
    
    def server_handler(msg):
        print ("Server Msg:", msg.typeName, "-", msg)
    
    
    def create_contract(symbol, sec_type, exch, prim_exch, curr):
    
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = sec_type
        contract.m_exchange = exch
        contract.m_primaryExch = prim_exch
        contract.m_currency = curr
        
        return contract
    
    def create_order(order_type, quantity, action):
    
        order = Order()
        order.m_action = action
        order.m_orderType = order_type
        order.m_totalQuantity = quantity
        order.m_lmtPrice = price
    
        return order
     
    #if __name__ == "__main__":
    
    client_id = 128
    order_id = 488## iterate order id
    port = 7496
    tws_conn = None
    
    #try:
    # Establish connection to TWS.
    tws_conn = Connection.create(port=port, clientId=client_id)
    tws_conn.connect()
        
    # Assign error handling function.
    tws_conn.register(error_handler, 'Error')
    
    # Assign server messages handling function.
    tws_conn.registerAll(server_handler)
    
    # Create AAPL contract and send order
    contract = create_contract(stock,'STK','SMART','SMART','USD')
    
    # Go long 100 shares of AAPL
    tws_order = create_order(ordertype, quantity, direction)
    
    # Place order on IB TWS.
    tws_conn.placeOrder(order_id, contract, tws_order)
    
    #finally:
    
    # Disconnect from TWS
    
    if tws_conn is not None:
        tws_conn.disconnect()
