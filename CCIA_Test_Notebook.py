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
#Import the data
ccia_df = dblgr.import_LGR(ccia_file)
db_df = dblgr.import_DB(DB_file)

#Set beginning and end times of the data you wish to view and analyze
begin = '2023-02-16 11:00:00'
end = '2023-02-16 13:00:00'

# %% [markdown]
# ## Plot the data
# This cell plots the data in three stacked plots. The top shows the LGR data, the middle shows the Dirtburner data, and the bottom plots them both. These are time series - pCO2 plotted on time. There is a difference in the heights of the curves (see bottom plot) and a slight offset in the peaks. The offset could be because the example doesn't have the exact time offset between the instruments (see the line of code that plots on `ax1[2]`, the bottom axes). However, this is a useful observation because there should be a small time offset between the two instruments as it takes some time for the gas to cross from the Dirtburner CO<sub>2</sub> analyzer to the LGR analyzer. We can use the Tmax function to calculate the actual time offset in both runs. 

# %%
CO2_view = dblgr.view_concentrations(ccia_df, db_df, begin, end, 0)

# %% [markdown]
# ## Analyze the Data
#
# Several questions arose from the first few runs. How do we assess the open split versus the metering valve to acquire isotope data? Even though the trends between instruments are the same, how do we account for the differences in absolute concentration measured by both of them? Ultimately, which technique is best to supply real-time isotope data that may inform sampling of the gas stream for $^{14}C $ data?
#
# To get at most of these questions, we have to probe and analyze the data. Remember, the LGR data, for example, has 105 individual data streams (columns) and we have only accessed 2 so far above. Now we need to probe the isotope data and start to think about statistical tests as well as qualitative tests that will help us understand these questions. We also need to compare these data between different runs and not necessarily between instruments. 
#
# Given that the data streams above qualitatively match, we will use mainly LGR data below. Using the LGR data ensures that the isotope and concentration data match point for point because they were recorded in the same instrument. It also simplifies comparisons in terms of time, however we will need to use elapsed time. We may need to access temperature too, if timings are not well recorded in the run sheets, but we'll cross that bridge when we come to it. Crossing 2 data streams is not always easy, in fact it is almost always troublesome.

# %%
#Plot the isotope trends from two runs

#Import the two runs you want to compare, and name the dataframes descriptively to avoid confusion:
db_2274_ccia_df = dblgr.import_LGR('ccia_10Feb2023_f0000.txt')
db_2275_ccia_df = dblgr.import_LGR('ccia_16Feb2023_f0000.txt')

#Define beginning and end of each run:
begin_2275 = begin #(These should be the same as the ones used up above, change accordingly if you are using different runs!)
end_2275 = end
begin_2274 = pd.to_datetime('2023-02-10 09:05:00')
end_2274 = pd.to_datetime('2023-02-10 11:34:00')

#Mask the data from each run that you want to visualize
db_2274_ccia_run_df = db_2274_ccia_df.loc[(db_2274_ccia_df['Time']>begin_2274) & (db_2274_ccia_df['Time']<end_2274)]
db_2275_ccia_run_df = db_2275_ccia_df.loc[(db_2275_ccia_df['Time']>begin_2275) & (db_2275_ccia_df['Time']<end_2275)]

db_2274_ccia_run_df['Elapsed Time'] = [pd.Timedelta(time-min(db_2274_ccia_run_df['Time']), unit='seconds') for time in db_2274_ccia_run_df['Time']] 
db_2275_ccia_run_df['Elapsed Time'] = [pd.Timedelta(time-min(db_2275_ccia_run_df['Time']), unit='seconds') for time in db_2275_ccia_run_df['Time']] 


#Plot the data on those elapsed time axes:
db_2274_ccia_run_df.plot(x='Elapsed Time', y='d13C', color='lavender', ylabel=r'$\delta ^{13}C$, relative')
db_2275_ccia_run_df.plot(x='Elapsed Time', y='d13C', color='lightgreen', ylabel=r'$\delta ^{13}C$, relative')



# %% [markdown]
# ## Interpretation
# Somehow, the masking of run DB-2274 is not working and I am not sure why. That is posing the problem of no data in the top plot above. Furthermore, the elapsed time axis is posing problems because it limits plotting to pandas rather than in matplotlib which evidently cannot handle pandas timestamps. I will continue to troubleshoot these problems, but the goal was to get both plots on the same axes, which is not possible in pandas.plot(). 
