from brownie import accounts, config, network, interface
from scripts.aave_interaction import aave_deposit, aave_borrow, get_amount_to_borrow
from web3 import Web3

#######################################################################
#
# Main script for automated depositing all available WETH to AAVE
# and borrowing 0.8 of available to borrow DAI
# (it means 0.64 of current ETH price in DAI for WETH max LTV is 0.8).
#
# This script is meant to used for Polygon chain
#
#######################################################################

def main():
    # Actual metamask account
    account = accounts.load('metamask-main')

    weth_token_address = config['networks'][network.show_active()]['weth_token']
    dai_token_address = config['networks'][network.show_active()]['dai_token']
    weth = interface.IERC20(weth_token_address)
    dai = interface.IERC20(dai_token_address)
    
    amount_to_deposit = weth.balanceOf(account.address)
    formatted_to_deposit = Web3.fromWei(amount_to_deposit, 'ether')
    print(f'You can deposit {formatted_to_deposit} WETH')

    deposit_transaction = aave_deposit(account, weth_token_address, amount_to_deposit)
    deposit_transaction.wait(1)

    max_ltv_fraction = 0.8
    amount_to_borrow = get_amount_to_borrow(account, dai_token_address, max_ltv_fraction)
    formatted_to_borrow = Web3.fromWei(amount_to_deposit, 'ether')
    print(f'You can borrow {formatted_to_borrow} DAI')

    borrowing_transaction = aave_borrow(account, dai_token_address, amount_to_borrow)
    borrowing_transaction.wait(1)
    print('Dai successfully borrowed!')

    dai_balance = Web3.fromWei(dai.balanceOf(account.address), 'ether')
    print(f'Now you have {dai_balance} DAI!')
