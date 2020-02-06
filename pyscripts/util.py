import re
import os
from datetime import datetime as dt

from pyscripts import (
    dbms as sql
)

'''
Loads the most recent save state and returns the last modified time of the most recently parsed AppData.lua data and
the path of the AppData.lua file (your World of Warcraft directory). If there is no saved data, triggers user to input
path of World of Warcraft directory and sets last modified time to the oldest time Python allows.
'''
def loadState():
    print('Searching for AppData.lua path and last modified time....')
    # If AppData path is saved, read file. If not, prompt user to input World of Warcraft directory folder.
    ad_path = ''
    try:
        with open('bin/adp.bin', 'rb') as file:
            ad_path_byte = file.read()
        ad_path = ad_path_byte.decode()
    except FileNotFoundError as e:
        while ad_path == '':
            print('Please copy and paste World of Warcraft folder path in the format "<path to wow folder>/World of Warcraft"')
            ad_path = input('Path: ')

            # If extra directories to path are added, remove back to World of Warcraft directory
            try:
                ad_path = re.search('(.*?)World of Warcraft', ad_path).group()
            except NoneTypeError as e:
                ad_path = ''
                continue

            # If user input incorrect path, prompt user to input path again
            if not os.path.exists(ad_path):
                ad_path = ''
                print('Directory does not exist. Unable to locate World of Warcraft folder.')
                continue

            # If TradeSkillMaster_AppHelper addon is not installed, prompt user to install addon and quit.
            ad_path += '/_classic_/Interface/AddOns/TradeSkillMaster_AppHelper'
            print(ad_path)
            if not os.path.exists(ad_path):
                ad_path = ''
                raise FileNotFoundError("""
                Unable to locate TradeSkillMaster_AppHelper.
                Please download TradeSkillMaster_AppHelper at https://www.tradeskillmaster.com/install
                """)

            # If there is no AppData file, TradeSkillMaster_AppHelper is corrupted and needs to be reinstalled
            ad_path += '/AppData.lua'
            if not os.path.isfile(ad_path):
                ad_path = ''
                raise FileNotFoundError('Unable to access data. Please reinstall TradeSkillMaster_AppHelper.')

    # Load modified time from most recent parsed data. If there is no recent parsed data, set to earliest possible
    # date.
    try:
        with open('bin/lfm.bin', 'rb') as file:
            lst_mod_byte = file.read()
        lst_mod = dt.strptime(lst_mod_byte.decode(), '%Y-%m-%d %H:%M:%S.%f')
    except FileNotFoundError as e:
        lst_mod = dt.min

    print('Successfully loaded AppData.lua path and last modified time.')

    print('Searching for saved database information...')
    # Load sql database information
    try:
        with open('bin/dbms.bin', 'rb') as file:
            sql_byte = file.read()

        print('Loading database information...')
        db, usr, pw, host, port = sql_byte.decode().split(',')
        db, usr, pw, host, port = sql.testConnection(db, usr, pw, host, port)
    except FileNotFoundError as e:
        print('No database information found.')
        db, usr, pw, host, port = sql.testConnection()


    return ad_path, lst_mod, db, usr, pw, host, port


'''
Saves the state of the most recently run data scan to bin files.
'''
def saveState(lst_mod, ad_path, db, usr, pw, host, port):
    print("Saving most recent AppData.lua information.")

    # Convert date to binary, and store in bin file
    lst_mod_byte = lst_mod.strftime('%Y-%m-%d %H:%M:%S.%f')
    lst_mod_byte = lst_mod_byte.encode('utf-8')
    with open('bin/lfm.bin', 'wb') as file:
        file.write(bytearray(lst_mod_byte))

    # Convert path to binary and store in bin file
    ad_path_byte = ad_path.encode('utf-8')
    with open('bin/adp.bin', 'wb') as file:
        file.write(bytearray(ad_path_byte))

    if host != '':
        sql_str = db + ',' + usr + ',' + pw + ',' + host + ',' + port
        sql_byte = sql_str.encode('utf-8')
        with open('bin/dbms.bin', 'wb') as file:
            file.write(bytearray(sql_byte))

    return


'''
Scans through TradeSkillMaster_AppHelper directory and cleans any conflicting files (For if the user is keeping files
on multiple computers). Keeps the most recent AppData.lua file.
'''
def cleanAppData(path):
	data_dir = os.path.dirname(path)

	# Find all conflicted AppData files
	data_files = os.listdir(data_dir)
	appdata_list = []
	for file in data_files:
		if re.match('AppData', file) is not None:
			appdata_list.append(file)


	if len(appdata_list) > 1:
		print("Found {0} AppData.lua files. Removing all but most recent file.".format(len(appdata_list)))

		# Find the most recent AppData file
		recmod = ''
		recmod_time = dt.min
		for file in appdata_list:
			file_ts = dt.fromtimestamp(os.path.getmtime(data_dir + '/' + file))
			if file_ts > recmod_time:
				recmod_time = file_ts
				recmod = file

		# Move all AppData files that are not the most recent
		for file in appdata_list:
			if file != recmod:
				os.remove(data_dir + '/' + file)

		# Rename the most recent AppData file to AppData.lua
		os.rename(data_dir + '/' + recmod, data_dir + '/AppData.lua')

	return