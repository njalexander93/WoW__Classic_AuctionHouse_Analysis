import psycopg2 as sql
from datetime import datetime as dt

def testConnection(db='', usr='', pw='', host='', port=''):
    while 1:
        if host == '':
            print("Please enter Postgresql DBMS information. If you choose not to connect to a postgres database, enter 'q' for host.")
            host = input('Host: ')

            if host.lower() == 'q':
                print('Bypassing sql database information. All data will be saved in a csv file located in the data directory.')
                return '', '', '', ''

        if port == '':
            port = input('Port: ')

        if db == '':
            db = input('Database: ')

        if usr == '':
            usr = input('Username: ')

        if pw == '':
            pw = input('Password: ')

        print('Testing connection...')
        try:
            conn = sql.connect(dbname=db, user=usr, password=pw, host=host, port=port)
            print('Test connection successful!')
            conn.close()
            return db, usr, pw, host, port
        except:
            print('Unable to reach host {0}'.format(host))
            db, usr, pw, host, port = ('', '', '', '', '')
            continue


def insertNewData(df, db, usr, pw, host, port):
    print("Attempting to connect to host {0}".format(host))
    try:
        conn = sql.connect(dbname=db, user=usr, password=pw, host=host, port=port)
    except:
        print('Unable to reach host {0}'.format(host))
        return
    print("Connection Successful!")
    cur = conn.cursor()

    with open('sqlscripts/rec_scantime.sql') as file:
        script = file.read()
    cur.execute(script)
    max_time = cur.fetchall()[0]
    max_time = max_time[0]

    scan_time = max(df.scanTime.tolist())
    if scan_time > max_time:

        col_string = ""
        for col in df.columns.tolist():
            col_string += col + ", "
        col_string = col_string[:-2]

        data_string = ""
        for i in range(len(df)):
            data_string += '('
            for j in range(len(df.columns)):
                if j == len(df.columns) - 1:
                    data_string += "to_timestamp('{0}','YYYY-MM-DD HH24:MI:SS')".format(df.iloc[i, j]) + "),\n"
                else:
                    data_string += str(df.iloc[i, j]) + ', '
        data_string = data_string[:-2]

        with open('sqlscripts/insert_data.sql') as file:
            script = file.read().format(col_string, data_string)
        try:
            log = cur.execute(script)
            conn.commit()
            print("Data successfully uploaded on {0}".format(dt.now()))

            with open('sqlscripts/rec_scantime.sql') as file:
                script = file.read()
            cur.execute(script)
            max_time = cur.fetchall()[0]
            max_time = max_time[0]

            if max_time != scan_time:
                print('Table insert failed.')
                print('Max DBMS time: {0}'.format(max_time))
                print('Time of scan: {0}'.format(scan_time))
        except:
            print("Unable to insert new data.")
            return
    else:
        print("No new data to insert.")

    conn.close()
    return