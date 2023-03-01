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
    a = [timestamp.strftime('%Y-%m-%d %H:%M:%S') for timestamp in ccia_df['Time']]
    ccia_df['Time'] = pd.to_datetime(a)


    return ccia_df

def convert_dates(df):
    '''Convert the dates in date_tiem column from LabView to EST.
    '''
    debug('Operating in debug mode.', '\n')
   # set time zone relative to GMT
    dh = -5  # EST
    dy = -66  # to deal with LabView's 65 year and 40 week future offset

    # make 'date_time' column into timestamp
    #- pd.Timedelta(weeks=dy*52-12, hours=dh)
    df['Time'] = pd.to_datetime(
        df['Time'],
        origin='unix',
        unit='s'
    )  + pd.Timedelta(weeks=dy*52-12+1/7, hours=dh)
    
   

    return df

def view_concentrations(ccia_df, db_df, begin_timestamp, end_timestamp, time_offset):
    '''
    Initial data view comparison of the [CO2] data in the dirtburner and in the LRG CCIA.
    This function takes the two dataframes, two timestamps marking the beginning and end of 
    the data gathering period, and plots the data in a 3-panel plot. The time offset is for 
    adjusting the time if the computers are registering different times for the duration of the runs

        Inputs:
            ccia_df (dataframe) - the output of the import_LGR function. A dataframe with 105 columns rows 
                from approximately every second of data acquisition.
            db_df (dataframe) - the output of the import_DB function. A dataframe with 7 columns and rows
                from approxaimtely every second of data acquisition.
            begin_timestamp (pandas timestamp) - a string in the format 'YYYY-mm-dd HH:MM' to mark the beginning
                of the experiment
            end_timestamp (pandas timestamp) - a string in the format 'YYYY-mm-dd HH:MM' to mark the end
                of the experiment
            time_offset (floating point number) - The number of hours of offset there is between the CCIA and 
                DB computer, if there is any offset. Good laboratory practice would be to ensure that there is 
                no offset, however this allows you to adjust for instance, if you have to reboot the linux system
                controlling the LGR CCIA system.
        
        Outputs:
            ax1 (matplotlib axes handle) - this is the handle returned so that you can make changes to the axes
                (axis labels, fonts, etc.) after using the function. There are three axes, 0 is the top and 2 
                is the bottom


    '''
    #Mask the dataframes to isolate only the data that the viewer wants to view. 
    begin = pd.to_datetime(begin_timestamp)
    end = pd.to_datetime(end_timestamp)
    ccia_run_df = ccia_df.loc[(ccia_df['Time']>begin) & (ccia_df['Time']<end)]
    db_run_df = db_df.loc[(db_df['Time']>begin) & (db_df['Time']<end)]
    
    del_time = pd.Timedelta(hours=time_offset) #This accounts for any difference in times between the computers.
    fig1, ax1 = plt.subplots(nrows=3, ncols=1, sharex=True)
    ax1[0].plot(ccia_run_df['Time'] - del_time, ccia_run_df['[CO2]_ppm'])
    ax1[0].set(title='LGR')
    ax1[1].plot(db_run_df['Time'], db_run_df['pCO2'], color='peru')
    ax1[1].set(title='DB')
    plt.xticks(rotation=30, ha='right')
    ax1[2].plot(ccia_run_df['Time'] - del_time, ccia_run_df['[CO2]_ppm'])
    ax1[2].plot(db_run_df['Time'], db_run_df['pCO2'], color='peru')

    ax1[2].set(xlabel='Time', title='DB and LGR')
    big_ax1 = fig1.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    big_ax1.set(ylabel=r'pCO$_{2}$, ppm')

    return ax1
