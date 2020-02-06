import os
import time
from datetime import datetime as dt

from pyscripts import(
	util,
	appdata as ap,
	dbms as sql
)

if __name__ == '__main__':
	# Init last lst_modification and the AppData.lua path at start of program
	ad_path, lst_mod, db, usr, pw, host, port = util.loadState()

	# Infinite loop to keep script running indefinitely
	while 1:
		# Clean any conflicting AppData.lua files
		util.cleanAppData(ad_path)

		# If the most recent modification is more recent than the last parsed data, parse data and merge with old data
		try:
			if lst_mod < dt.fromtimestamp(os.path.getmtime(ad_path)):
				# Parse the new data from the most recent lua file
				new_data = ap.parseAppData(ad_path)

				if new_data.empty:
					time.sleep(1)
					continue

				# If saving to csv, merge data with old data in csv file. If using a postgresql database, insert new
				# data into database
				if host == '':
					ap.mergeNewData(new_data)
				else:
					sql.insertNewData(new_data, db, usr, pw, host, port)

				# Save state in case of server failure
				lst_mod = dt.fromtimestamp(os.path.getmtime(ad_path))
				util.saveState(lst_mod, ad_path, db, usr, pw, host, port)

				print('Done.')
		except FileNotFoundError as e:
			print("FileNotFoundError: {0}".format(e))
			print('Buffering for 10 seconds to catch up with file space...')
			time.sleep(10)
			print('Buffering complete. Continuing scan.')
			continue

		# Sleep for 1 second to avoid system overload
		time.sleep(1)