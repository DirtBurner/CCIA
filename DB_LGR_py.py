import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print('%%%%%%%%% Dirtburner - Flow-through LGR Data Visualization %%%%%%%%%%%%')

#To turn on debugging, do this in your code:
    #import process_db as DB
    #DB.DEBUG = True
    #Change this variable to True to debug any functions in the DB package. Enter this line in any cell to debug code in that cell.
DEBUG = False

def debug(*args):
    """Call print() with arguments if DEBUG is True""" # preserves formatting
    if DEBUG == True:
        print(*args)


def import_DB(file):
    db_df = pd.read_csv(
        file,
        delimiter='\t',
        header=None, 
        names=[
            'Time',
            'pCO2',
            'Temperature',
            'He_main',
            'He_side',
            'O2'
        ]
    )

    db_df = convert_dates(db_df)

    return db_df

def import_LGR(file):
    ccia_df = pd.read_csv(
        file,
        skiprows=1,
        engine='python',
        skipfooter=283
    )

    col_names = [a.lstrip() for a in ccia_df.columns]
    ccia_df.columns = col_names
    ccia_df['Time'] = pd.to_datetime(ccia_df['Time'])


    return ccia_df

def convert_dates(df):
    '''Convert the dates in date_tiem column from LabView to EST.
    '''
    debug('Operating in debug mode.', '\n')
   # set time zone relative to GMT
    dh = -5  # EST
    dy = -66  # to deal with LabView's 65 year and 40 week future offset

    # make 'date_time' column into timestamp
    df["Time"] = pd.to_datetime(df["Time"], unit="s")

    # now get it into a meaningful time
    df["Time"] = df["Time"] + pd.Timedelta(weeks=dy*52-12, hours=dh)

    return df