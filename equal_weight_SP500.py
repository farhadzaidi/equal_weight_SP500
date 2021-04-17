import os
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup


# retrieve source using requests and turn it into BeautifulSoup object for parsing
source = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies').text
soup = BeautifulSoup(source, 'lxml')

# get table with S&P 500 companies
table = soup.find(id='constituents').find('tbody')
rows = table.find_all('tr')
# remove table header
del rows[0]

# get stock symbols from rows
symbols = []
for row in rows:
	symbols.append(row.td.a.text)


# use IEX API to get share prices for each stock
share_prices = []
comma_separated_symbols = ','.join(symbols)
API_URL = f'https://api.iextrading.com/1.0/tops/last?symbols={comma_separated_symbols}'
stocks = requests.get(API_URL).json()

for stock in stocks:
    share_prices.append(stock['price'])


# get user's portfolio size
invalid = True
while invalid:
	portfolio_size = input('What is the size of your protfolio (in USD)?')

	try:
		portfolio_size = float(portfolio_size)
		invalid = False
	except ValueError:
		print("That's not a number. Try again.")

invalid = True
while invalid:
    fractional_shares = input('Does your broker allow fractional shares (y/n)?')
    
    if fractional_shares == 'y' or fractional_shares == 'n':
        invalid = False
    else:
        print("Please enter 'y' or 'no'")


# calculate equal amounts per share based on user's portfolio size and the price of each share
amount_per_share = portfolio_size / len(symbols)
shares_per_stock = []
for share_price in share_prices:
	shares_per_stock.append(amount_per_share/share_price)

if fractional_shares == 'n':
    shares_per_stock = [int(i) for i in shares_per_stock]


# convert data into pandas DataFrame
indices = [i for i in range(1, 506)]
share_prices = [f'${i}' for i in share_prices]
chart_data = {
    'Symbol': symbols,
    'Price Per Share': share_prices,
    'Amount of Shares to Buy': shares_per_stock
}

chart = pd.DataFrame(data=chart_data, index=indices)

# convert data to xlsx
chart.to_excel('equal_weighted_SP500.xlsx', index=False)