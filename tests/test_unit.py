from scripts.aave_interaction import *
import pytest 
from brownie import network, accounts, config, interface
from web3 import Web3

def test_get_price():
    # Arrange 
    if network.show_active() == 'polygon-test':
       pytest.skip('Only for testnet testing')
    # Act
    price = get_price(
        config['networks'][network.show_active()]['weth_token']
    )
    print(price)
    # Assert
    assert price == Web3.toWei(1, 'ether')

def test_aave_deposit():
    # Arrange
    if network.show_active() == 'polygon-main':
        pytest.skip('Not for mainnet')

    account = accounts.add(config["wallets"]["from_key"])
    wmatic_address = config['networks'][network.show_active()]['wmatic_token'] 

    # Act
    amount = 0.1  # Instant sufficient amount 
    get_wmatic(account, amount)    
    aave_deposit(account, wmatic_address, Web3.toWei(amount, 'ether'))
    
    # Assert    
    wmatic_price = get_price(wmatic_address)
    total_collateral_eth =  get_user_account_data(account)['total_collateral_eth']
    total_collateral_wmatic = total_collateral_eth / wmatic_price
    assert total_collateral_wmatic >= amount

def test_get_amount_to_borrow():
    # Arrange
    account = accounts.add(config["wallets"]["from_key"])
    weth_address = config['networks'][network.show_active()]['weth_token']

    # Act
    amount_to_borrow = get_amount_to_borrow(account, weth_address, factor=0.98)

    # Assert
    max_ltv_wmatic = 0.65  # Maximum locked total value for WMATIC as collateral
    total_collateral_eth =  get_user_account_data(account)['total_collateral_eth']    
    assert amount_to_borrow < total_collateral_eth * max_ltv_wmatic

def test_aave_borrow():
    # Arrange
    if network.show_active() == 'polygon-main':
        pytest.skip('Not for mainnet')

    account = accounts.add(config["wallets"]["from_key"])
    dai_address = config['networks'][network.show_active()]['dai_token']

    # Act
    amount = get_amount_to_borrow(account, dai_address)
    aave_borrow(account, dai_address, amount)
    
    # Assert
    dai = interface.IERC20(dai_address)
    amount_borrowed = dai.balanceOf(account.address)    
    assert amount_borrowed >= amount
