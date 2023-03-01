# %% [markdown]
# # Working with CCIA and Dirtburner Data
# This `Jupyter notebook` serves to develop functions used for the comparative analysis of data from the Dirtburner and from the Los Gatos Research (LGR) flow-through carbon dioxide isotope analyzer. The following cells load packages, names files, import data, and plot a figure. 

# %%
#Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import DB_LGR_py as dblgr

# %% [markdown]
# ## Entering the file names
# In this cell, you simply need to enter the file names of the comparable runs. Each file name should include directory information with `/` between parent and progeny directories (if you paste a directory name it will have `\` and you will need to change those slashes) if the file is not in this directory. Each file name should include the proper extension. And each filename should be entirely within single or double quotes (to specify that it is a string). 
#
# Example: 
# * In this directory: `'my_ccia_file.txt'` is good. `'my_ccia_file'.txt` is not good.
# * In another directory: `'C/my_folder/my_file.txt'` is good. `'C\my_folder\my_file.txt'` is not good.
#
# Preloaded examples are available for you to see the formatting, but those files are in this repository directory. 

# %%
#To import data files, you need to enter their names as strings here:
DB_file = 'DB-2275-20230216.txt'
ccia_file = 'ccia_16Feb2023_f0000.txt'


# %% [markdown]
# ## Importing and masking data
# In the next cell, the first two lines import the data - one line each for the Dirtburner and the LGR. The remaining lines are masking the data. I will work on this second portion to make it simpler, i.e. requiring only limited python know-how. 
#
# Finally, the last run prints out the first 5 rows of the Dirtburner data. 

# %%
db_df = dblgr.import_DB(DB_file)
ccia_df = dblgr.import_LGR(ccia_file)
print(db_df.head())
print(type(db_df['Time'][0]))
#Mask the run for the only the data from the experimental time (between begin and end)
#We may be able to fold this into a function as well. 
begin = pd.to_datetime('2023-02-16 11:00:00')
end = pd.to_datetime('2023-02-16 13:00:00')
ccia_run_df = ccia_df.loc[(ccia_df['Time']>begin) & (ccia_df['Time']<end)]
db_run_df = db_df.loc[(db_df['Time']>begin) & (db_df['Time']<end)]
print(db_run_df.head())
print(ccia_df.shape)
print(ccia_run_df.columns[0:15]) #There are 105 columns of data in ccia_df. It is useful to know the first few.

# %% [markdown]
# ## Plot the data
# This cell plots the data in three stacked plots. The top shows the LGR data, the middle shows the Dirtburner data, and the bottom plots them both. These are time series - pCO2 plotted on time. There is a difference in the heights of the curves (see bottom plot) and a slight offset in the peaks. The offset could be because the example doesn't have the exact time offset between the instruments (see the line of code that plots on `ax1[2]`, the bottom axes). However, this is a useful observation because there should be a small time offset between the two instruments as it takes some time for the gas to cross from the Dirtburner CO<sub>2</sub> analyzer to the LGR analyzer. We can use the Tmax function to calculate the actualy time offset in both runs. 

# %%
#Make a plot, add time offset with pd.Timedelta function
#(This cell will be eventually made into one line of code when we decide what we want to plot.)

del_time = pd.Timedelta(hours=0) #This accounts for any difference in times between the computers.
fig1, ax1 = plt.subplots(nrows=3, ncols=1, sharex=True)
ax1[0].plot(ccia_run_df['Time'] - del_time, ccia_run_df['[CO2]_ppm'])
ax1[1].plot(db_run_df['Time'], db_run_df['pCO2'], color='peru')
ax1[2].plot(ccia_run_df['Time'] - del_time, ccia_run_df['[CO2]_ppm'])
ax1[2].plot(db_run_df['Time'], db_run_df['pCO2'], color='peru')


# %%
print(ccia_run_df.head())


# %%
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
    print('Time elapsed = ', (max(db_df['Time']) - min(db_df['Time']))/60, ' minutes')
    db_df = convert_dates(db_df)

    return db_df

def convert_dates(df):
    '''Convert the dates in date_tiem column from LabView to EST.
    '''
    #debug('Operating in debug mode.', '\n')
   # set time zone relative to GMT
    dh = -5  # EST
    dy = -66  # to deal with LabView's 65 year and 40 week future offset

    # make 'date_time' column into timestamp
    #- pd.Timedelta(weeks=dy*52-12, hours=dh)
    df['Time'] = [pd.to_datetime(time, unit='s', origin='unix') for time in db_df['Time']] 
    print(df['Time'][0:5])
    a = [timestamp.strftime('%Y-%m-%d %H:%M:%S') for timestamp in df['Time']]
    print(a[0:5])
    # now get it into a meaningful time
    df["Time"] = pd.to_datetime(a) 
    
    return df

test_df = import_DB(DB_file)
print(test_df.head())
print(type(test_df['Time'][0]))

# %%
t_df = pd.read_csv(
        DB_file,
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

print('Time elapsed = ', (max(t_df['Time']) - min(t_df['Time']))/60, ' minutes')
print(type(pd.to_datetime(t_df['Time'][0])))
t_df['Time'] = pd.to_datetime(t_df['Time'], origin='unix', unit='s') + pd.Timedelta(weeks=-66*52-12+1/7, hours=-6)
print(t_df.head())
