from brownie import network, accounts, interface, config
from web3 import Web3

##################################################################
# 
# Python scripts for automated reinvesting new crypto.
# This module implements investing in AAVE say WETH in Polygon
# and borroing say DAI of a specified amount safe enough for not being liquidated
# for farther investing in DiFi protocols say Balancer.
#
##################################################################

def aave_deposit(account, erc20_address, amount):
    lending_pool = get_lending_pool()
    tx = lending_pool.deposit(
        erc20_address,
        amount,
        account.address,
        0,
        {"from": account}
    )    
    tx.wait(1)
    return tx

def aave_borrow(account, erc20_address, amount):
    lending_pool = get_lending_pool()
    tx = lending_pool.borrow(
        erc20_address,
        amount,
        2,
        0,
        account.address,
        {"from": account}
    )
    tx.wait(1)
    return tx

def get_wmatic(account, amount):
    account = account
    wmatic = interface.IWETH(
        config['networks'][network.show_active()]['wmatic_token']
    )
    tx = wmatic.deposit({'from': account, 'value': Web3.toWei(amount, 'ether')})
    tx.wait(1)
    return tx

def approve_wmatic(account, spender_address):
    account = account
    wmatic = interface.IWETH(
        config['networks'][network.show_active()]['wmatic_token']
    )
    tx = wmatic.approve(
        spender_address, 
        Web3.toWei(1000000, 'ether'),
        {'from': account}
    )
    tx.wait(1)
    return tx

def get_user_account_data(account):
    lending_pool = get_lending_pool()
    user_account_data = lending_pool.getUserAccountData(account.address)
    result ={
        'total_collateral_eth': user_account_data[0],
        'total_debt_eth': user_account_data[1],
        'available_borrow_eth': user_account_data[2]
    }
    return result

# Returns ammount for borrowing of specified token 
# taking current address's collateral and a fraction of maximum amount available.
# *factor* must be less then 1 for transaction to pass
def get_amount_to_borrow(account, erc20_address, factor=0.8):
    if factor >= 1:
        return 0
    available_borrow_eth = get_user_account_data(account)['available_borrow_eth']
    price = get_price(erc20_address)
    amount_to_borrow = int((available_borrow_eth / price) * factor * 10**18)
    return amount_to_borrow

# Returns a Brownie contract of actual lending pool
# according to https://docs.aave.com/developers/v/2.0
def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_addresses_provider']
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    print(f'lending pool address: {lending_pool_address}')
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

# Returns a Brownie contract of actual price oracle
# according to https://docs.aave.com/developers/v/2.0
def get_price_oracle():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_addresses_provider']
    )
    price_oracle_address = lending_pool_addresses_provider.getPriceOracle()
    print(f'price oracle address: {price_oracle_address}')
    price_oracle = interface.IPriceOracleGetter(price_oracle_address)
    return price_oracle

# Returns curent price using AAVE's price oracle
def get_price(erc20_address):
    price_oracle = get_price_oracle()
    price = price_oracle.getAssetPrice(erc20_address)
    return price    
