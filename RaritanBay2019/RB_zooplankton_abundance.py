#!/usr/bin/env python
"""
Created on Apr 9 2020 by Lori Garzio
@brief Creates bar charts of zooplankton abundance
f: file containing zooplankton abundance data
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from brokenaxes import brokenaxes
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

f = '/Users/lgarzio/Documents/rucool/Saba/microplastics/RaritanBay/RaritanBay.xlsx'


def stacked_bar_chart(dataframe, group_list, column_name, bar_width, plot_title, sname, colors=None):
    fig, ax = plt.subplots()
    for ind in range(len(group_list)):
        sdf = dataframe[dataframe[column_name] == group_list[ind]]
        bar_data = np.array(sdf['abundance_count_per_m3'])

        if ind == 0:
            r = np.arange(len(sdf))
            if colors is not None:
                ax.bar(r, bar_data, width=bar_width, color=colors[ind], edgecolor='black', label=group_list[ind])
            else:
                ax.bar(r, bar_data, width=bar_width, edgecolor='black', label=group_list[ind])
            bottoms = bar_data
        else:
            if colors is not None:
                ax.bar(r, bar_data, width=bar_width, bottom=bottoms, color=colors[ind], edgecolor='black',
                       label=group_list[ind])
            else:
                ax.bar(r, bar_data, width=bar_width, bottom=bottoms, edgecolor='black', label=group_list[ind])
            bottoms = bottoms + bar_data

    ax.set_xticks(r)
    ax.set_xticklabels(sdf['CS'].tolist())
    ax.set_ylabel(r'Zooplankton abundance (ind $\rm m^{-3}$)')  # \rm removes the italics
    plt.title(plot_title)
    plt.legend(fontsize=8)

    plt_save = os.path.join(os.path.dirname(f), sname)
    plt.savefig(str(plt_save), dpi=150)
    plt.close


df = pd.read_excel(f, sheet_name='abundance')
df.sort_values(by='CS', inplace=True)  # make sure the stations are in alphabetical order
df['species_display'] = ''

for i, row in df.iterrows():
    # shorten copepod species names
    if 'Copepod' in row['type']:
        df.loc[i, 'species_display'] = '. '.join((row['species'].split(' ')[0][0], row['species'].split(' ')[1]))
    else:
        df.loc[i, 'species_display'] = row['species']

stns = np.unique(df['CS']).tolist()

# bar chart with location on x-axis, inside and outside front only
width = 0.4

# bar chart with station on x-axis
df_copes = df[df['type'] != 'Other']
species = np.unique(df_copes['species_display']).tolist()
cols = cm.tab20(np.linspace(0, 1, len(species)))
plt_ttl = 'Spring 2019 Copepods'
stacked_bar_chart(df_copes, species, 'species_display', width, plt_ttl, 'zooplankton_abundance1.png', cols)

# bar chart with location on x-axis, copepod groups
df_copes = df[df['type'] != 'Other']
df_copes_type = df_copes.groupby(['CS', 'type']).sum().reset_index()
types = np.unique(df_copes['type']).tolist()
stacked_bar_chart(df_copes_type, types, 'type', width, plt_ttl, 'zooplankton_abundance2.png')

# bar chart with location on x-axis, A. tonsa only
df_atonsa = df[df['species_display'] == 'A. tonsa']
species = np.unique(df_atonsa['species_display']).tolist()
plt_ttl = 'Fall 2019 - Acartia tonsa'
stacked_bar_chart(df_atonsa, species, 'species_display', width, plt_ttl, 'zooplankton_abundance_atonsa.png')