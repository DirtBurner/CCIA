# %% [markdown]
# # Working with CCIA and Dirtburner Data
# This `Jupyter notebook` serves to develop functions used for the comparative analysis of data from the Dirtburner and from the Los Gatos Research (LGR) flow-through carbon dioxide isotope analyzer. The following cells load packages, names files, import data, and plot a figure. 

# %%
#Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.lines as mlines
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
DB_file = 'DB-2277-20230328.txt'
ccia_file = 'ccia_28Mar2023_f0000.txt'


# %% [markdown]
# ## Importing and masking data
# In the next cell, the first two lines import the data - one line each for the Dirtburner and the LGR. The remaining lines are masking the data. I will work on this second portion to make it simpler, i.e. requiring only limited python know-how. 
#
# Finally, the last run prints out the first 5 rows of the Dirtburner data. 

# %%
#Import the data
ccia_df = dblgr.import_LGR(ccia_file)
db_df = dblgr.import_DB(DB_file)
#print(db_df.tail())

#Set beginning and end times of the data you wish to view and analyze
begin = '2023-03-28 8:30:00'
end = '2023-03-28 10:30:00'

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
#Set timestamps for beginning and end of each reaction you want to plot - no way around this, this has to come from your lab book and then has
#to be tuned based on the plots. 
begin_2274 = pd.to_datetime('2023-02-10 09:52:00')
end_2274 = pd.to_datetime('2023-02-16 11:34:00')
begin_2275 = pd.to_datetime('2023-02-16 10:50:00')
end_2275 = pd.to_datetime('2023-03-28 08:40:00')
begin_2277 = pd.to_datetime('2023-03-28 10:40:00')
end_2277 = pd.to_datetime('2023-03-28 13:00:00')
begin_2278 = pd.to_datetime('2023-04-06 10:33:00')
end_2278 = pd.to_datetime('2023-04-06 13:00:00')

#Use function to compare runs. Create lists of run files, timestamps, colors (that you want to plot), and legend labels, making sure they are in the same order
runs = ['ccia_10Feb2023_f0000.txt','ccia_16Feb2023_f0000.txt','ccia_28Mar2023_f0000.txt','ccia_06Apr2023_f0001.txt']
timestamps = [(begin_2274, end_2274), (begin_2275, end_2275), (begin_2277, end_2277), (begin_2278, end_2278)]
colors = ['gold', 'darkgreen', 'purple', 'plum']
legend_labels = [r'DB-2274, 211$\mu$mol, 15.03 Torr', r'DB-2275, 227$\mu$mol, 8 Torr', r'DB-2277, open split 75 mL/min', r'DB-2278, open split 125 mL/min']

#Use new function to plot runs comparatively, note use of keyword argument to change from the default of a d13C plot
ax1 = dblgr.compare_CCIA(runs, timestamps, colors, legend_labels)
ax2 = dblgr.compare_CCIA(runs, timestamps, colors, legend_labels, column_name='[CO2]_ppm')


# %% [markdown]
# ## Interpretation
# Surprise, surprise! The biggest difference between these two runs was that we choked the valve down halfway for run `DB-2275`. That seemed like a large change, but the frame work of *Poiseuille's Law* suggested that it was actually quite a small change given the large pressure at the inlet (flow controller side) of the instrumentation. However, we do these experiments for a reason. The data show that there was a profound effect on both the sensitivity (ability to show isotope change of two materials) and the isotope ratio. The former is surprising given the *Poiseuille's Law* framework. The latter is bizarre and needs more experimentation to iron out. But ultimately, the LGR is sensitive to small changes in the choke valve configuration. 
#
# ### *Isotope data*
# The isotope data shows that both the cellulose (first 2 peaks) and the calcium carbonate (last peak) are isotopically lighter than the carrier gas CO<sub>2</sub>. This likely means that the carrier gas CO<sub>2</sub> is near or slightly greater than the value of PDB, the international standard for carbon isotope values. This is a valuable piece of information that we will try to improve as the semester moves along. One can see the negative deviation in the isotope values of both runs, although it is smaller than the noise level for run DB-2274. Future experiments should choke the outlet valve further and compare to the open split with the choke valve fully open. 
#
# ### *Concentration data*
# The concentration data are less noisy than the isotope data. The peaks line up nicely once the starting time for each reaction is accurate. Similarly to the isotope data, the baseline is shifted in the run where we choked the outlet valve. In this case, the baseline is elevated. Does this make sense? We did not change the rate of supply of products from the reaction, nor did we change the reaction. Effectively, by decreasing the pump conductance by choking the outlet valve, we increased the pressure and the residence time of CO<sub>2</sub> molecules in the optical cell. However, the same can be said of He atoms. So, how did the concentrations increase for run DB-2275? We will need to see how the open split affects this moving forward in order to better understand it. A question of high importance is whether this elevated concentration baseline relates to the decreased isotope baseline in run DB-2275. 

# %%
df = dblgr.import_LGR('ccia_06Apr2023_f0001.txt')
_, _, new_df = dblgr.isotope_concentration_plot(df, -40, 2, 2.75, (begin_2278, end_2278),color_map='plasma', null_color='k')

