import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

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

def compare_CCIA(runs, timestamps, colors, legend_labels, column_name='d13C'):
    '''
    Function to compare different CCIA runs. User chooses colors, run files, timestamps, and column to plot. Function
    computes elapsed time for each run and plots on time axis. DB data files are not used, this should only be pointed 
    at CCIA files. 

        Inputs:
            runs (list of strings): List of file names, including extension, of the files (runs) you want to compare
            timestamps (list of tuples of strings): List of tuples, each containing the begin time and end time of a reaction
                entered as strings. Format should be 2023-02-10 09:52:00 (YYYY-MM-DD HH:mm:SS). 
            colors (list of strings): Strings for named colors in python Matplotlib
            legend_labels (list of strings): String to describe each run as you want in the figure legend.
            col (string): column you wish to plot. Columns must match those available in call to df.columns function, or will default
                to plotting the d13C column
    '''

    fig, ax = plt.subplots(nrows=1, ncols=1)
    label_list = []
    for j, run in enumerate(runs):
        #import each run
        df = import_LGR(run)
        if column_name not in df.columns:
            print('!! Specified column, ', column_name, ', is not in ', run, '. Defaulting to plot of d13C vs. elapsed time for this run. !!')
            plot_column = 'd13C'
        else:
            plot_column = column_name
        #set up begin and end
        begin = pd.to_datetime(timestamps[j][0]) 
        end = pd.to_datetime(timestamps[j][1])
        masked_df = df.loc[(df['Time']>begin) & (df['Time']<end)]
        #Calculate elapsed time
        masked_df.loc[:, 'Elapsed Time'] = [pd.Timedelta(time-masked_df['Time'].iloc[0], unit='seconds').total_seconds() for time in masked_df['Time']]
        ax.plot(masked_df['Elapsed Time'], masked_df[plot_column], color=colors[j])
        #Create legend label list
        label_list.append(mlines.Line2D([], [], color=colors[j], label=legend_labels[j]))

    #Choose column name:
    if column_name == 'd13C':
        y_label = r'$\delta^{13}$C, relative'
    elif column_name == '[CO2]_ppm':
        y_label = r'[CO$_{2}$], ppm'
    else:
        y_label = column_name
    ax.set_xlabel('Elapsed time, s')
    ax.set_ylabel(y_label)
    plt.legend(handles=label_list)
    
    return ax

def frac_calc(CO2_conc, bkgnd_conc):
    '''
    Calculate the fraction of the gas that was sample after subtracting that which is the carrier gas
        Inputs:
            CO2_conc (float): the concentration data from the LGR-CCIA
            bkgnd_conc (float, constant): the concentration of CO2 that represents no sample gas mixed in, generally the minimum of the 
                concentration from the LGR-CCIA data
        Outputs:
            frac_sam (float): number between 0 and 1 representing the proportion of sample
    '''
    frac_sam = (CO2_conc-bkgnd_conc)/CO2_conc

    return frac_sam

def delta_calc(delta_meas, baseline, f_sam):
    '''
    Calculate the delta value of the sample based on the assumed/know delta value of the carrier gas, the fraction of sample, and the measured
    delta value from the LGR-CCIA data
        Inputs:
            delta_meas (float): isotope data from the LGR-CCIA data file
            baseline (float, constant): assumed or measured stable isotope value of the carrier gas
            f_sam (float): output of frac_calc function, fraction of the sample in the [CO2] concentration
        Outputs: delta_sam (float): calculated delta value of the sample mixed with the carrier gas 
    '''
    if f_sam <= 0:
        delta_sam = baseline
    else:
        delta_sam = (delta_meas - baseline)/f_sam - baseline

    return delta_sam

def isotope_concentration_plot(df, delta_baseline, delta_meas_uncertainty, delta_calc_threshold, timestamps, color_map='plasma', null_color='k'):
    '''
    Plots a concentration vs. time plot, and colors the points with calculated isotope values. The calculation of 
    isotope values depends on an assumption that the minimum concentration of the run is the baseline value
    and any elevation in [CO2] is due to admixture of the sample. The calculation involves the fraction of sample
    in the denominator, so at low values (just above baseline), the calculated isotope values can be 
    erroneously high. To avoid this, the function asks you to enter the uncertainty on isotope measurements
    as well as what uncertainty you are willing to work with on the calculation. The lower the concentration, the
    higher the uncertainty with this instrument. The value you pick for delta_calc_threshold would be positive,
    and always moe than delta_meas_uncertainty. The closer these values are to one another, the more
    data will be masked black. 
        Inputs:
            df (dataframe): Dataframe loaded from the import_LGR function
            delta_meas_uncertainty (float): Assumed or known uncertainty on an isotope measurement of the LGR-CCIA
            delta_calc_threshold (float): Your level of acceptable uncertainty (in permil) of the calculated 
                isotope value of the sample. 
            timestamps (tuple of strings): a tuple in the form of (begin, end) where both beginning and end
                are strings in the format of YYYY-MM-DD HH:mm:SS
            color_map (matplotlib color map, string): a string representing the desired existing colormap
                recognized by matplotlib.pyplot. Default is plasma
            null_color (single matplotlib color string): string representing a single named color in Python
                This color will mark the points that have uncertainties beyond your threshold. Default = k
        

    '''
    #Add columns to the dataframes for both the fraction (first function above) and the delta value of the sample (second function)
    min_conc = min(df['[CO2]_ppm'])
    fraction_list = [frac_calc(a, min_conc) for a in df['[CO2]_ppm']]
    df.loc[:,['frac_sam']] = fraction_list
    delta_list = [delta_calc(a, delta_baseline, b) for a, b in zip(df['d13C'], df['frac_sam'])]
    df.loc[:,['delta_sam']] = delta_list
    #Calculate elapsed time and make new column
    begin = pd.to_datetime(timestamps[0]) 
    end = pd.to_datetime(timestamps[1])
    masked_df = df.loc[(df['Time']>begin) & (df['Time']<end)]
    masked_df.loc[:, 'Elapsed Time'] = [pd.Timedelta(time-masked_df['Time'].iloc[0], unit='seconds').total_seconds() for time in masked_df['Time']]

    #Split dataframe into that which can be plotted as an isotope value, and that which cannot
    iso_df = masked_df.loc[delta_meas_uncertainty/df['frac_sam']<delta_calc_threshold]
    debug(iso_df['frac_sam'].shape)
    no_iso_df = masked_df.loc[delta_meas_uncertainty/df['frac_sam']>=delta_calc_threshold]
    debug(no_iso_df['frac_sam'].shape)
    df_out = df

    #Plot concentrations, colored with isotope values (values with uncertainties > delta_calc_threshold are black dots)
    scat_fig, scat_ax = plt.subplots(nrows=1, ncols=1)
    g = scat_ax.scatter(iso_df['Elapsed Time'], iso_df['[CO2]_ppm'], s=10, c=iso_df['delta_sam'], cmap=color_map)
    scat_ax.plot(no_iso_df['Elapsed Time'], no_iso_df['[CO2]_ppm'], marker='.', mec=null_color, linestyle='', mfc='None')
    #scat_ax.annotate(r'Carrier gas $\delta^{13}$C = ' + str(delta_baseline) + '/n', )
    cbar = scat_fig.colorbar(g)
    scat_ax.set_ylabel(r'[CO$_{2}$], ppm')
    scat_ax.set_xlabel('Elapsed time, s')
    cbar.set_label(r'$\delta^{13}$C, calculated')

    return scat_ax, cbar, df_out
