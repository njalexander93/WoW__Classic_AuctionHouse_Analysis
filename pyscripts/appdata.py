import pandas as pd
import re
from datetime import datetime as dt


'''
Parses the AppData.lua file for all scan data from the most recent Auction House scan - Requires TMSApplication for
consistent up-to-date data.
'''
def parseAppData(path):
	print("Scanning new data from AppData.lua file....")

	with open(path, "r") as file:
		script = file.readlines()

	# Data we need is in the first line of the Interface\AddOns\TradeSkillMaster_AppHelper\AppData.lua file
	try:
		data_string = script[0]
	except IndexError as e:
		print("IndexError: {0}".format(e))
		print(script)
		return pd.DataFrame()



	print("Cleaning data and pushing to data frame...")
	# Extract scan time from script
	scan_time = re.search('downloadTime=[0-9]+', data_string).group()
	scan_time = int(re.search('[0-9]+', scan_time).group())
	scan_time = dt.fromtimestamp(scan_time)

	# Extract columns from script
	col = re.search('fields={(.*?)}', data_string).group()
	col = re.search('{(.*?)}', col).group()
	col = re.sub('[{}"]', '', col)
	col = re.sub('itemString', 'itemId', col)
	col = col.split(',')
	col.append('scanTime')

	# Extract data from script
	data = re.search('data={(.*?)}}', data_string).group()
	data = re.search('{{(.*?)}}', data).group()
	data = re.sub('[{}]{2}', '', data)
	data = data.split('},{')

	# Append data to data frame
	df = pd.DataFrame(columns=col)
	for d_string in data:
		row = d_string.split(',')
		row.append(scan_time)
		df.loc[len(df)] = row

	# Convert all columns to dtype int (except scan time)
	for c in col:
		if c != 'scanTime':
			df[c] = df[c].astype(int)

	return df


'''
Merges most recently parsed data with older data and stores in a csv file
'''
def mergeNewData(new_data):
	print("Merging new data with old data...")
	# If you do not have any stored data, create new file
	try:
		old_data = pd.read_csv('data/auction_data.csv')
	except FileNotFoundError as e:
		print("No auction_data.csv file found. Creating new file.")
		new_data.to_csv('data/auction_data.csv', index=False)
		return

	print('Saving data to auction_data.csv')
	# If parsed data is the most recent, append to old data and store
	recent_scan = max(pd.to_datetime(old_data.scanTime))
	if max(new_data.scanTime) > recent_scan:
		data = new_data.append(old_data)
		data.to_csv('data/auction_data.csv', index=False)

	return