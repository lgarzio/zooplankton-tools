#!/usr/bin/env python
"""
Created on Mar 24 2020 by Lori Garzio
@brief Creates a bar chart of zooplankton abundance
f: file containing zooplankton abundance data
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from brokenaxes import brokenaxes
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

f = '/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_zooplankton_abundance.xlsx'


def stacked_bar_chart(dataframe, group_list, column_name, bar_width, plot_title, sname, colors=None):
    fig, ax = plt.subplots()
    for ind in range(len(group_list)):
        sdf = dataframe[dataframe[column_name] == group_list[ind]]
        sdf.sort_values(by='station', inplace=True)  # make sure the stations are in alphabetical order
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
    ax.set_xticklabels(sdf['station'].tolist())
    ax.set_ylabel(r'Zooplankton abundance (ind $\rm m^{-3}$)')  # \rm removes the italics
    plt.title(plot_title)
    plt.legend(fontsize=8)

    plt_save = os.path.join(os.path.dirname(f), 'figures', sname)
    plt.savefig(str(plt_save), dpi=150)
    plt.close


df = pd.read_excel(f, sheet_name='abundance')
df['species_display'] = ''

for i, row in df.iterrows():
    # shorten copepod species names
    if 'Copepod' in row['type']:
        df.loc[i, 'species_display'] = '. '.join((row['species'].split(' ')[0][0], row['species'].split(' ')[1]))
    else:
        df.loc[i, 'species_display'] = row['species']

# grouped bar chart with species on x-axis
fig, ax = plt.subplots()
width = 0.25
outfr = df[(df['station'] == 'outside_front') & (df['type'] != 'Other')]
infr = df[(df['station'] == 'inside_front') & (df['type'] != 'Other')]
marine = df[(df['station'] == 'marine') & (df['type'] != 'Other')]

r1 = np.arange(len(outfr))
r2 = r1 + width
r3 = r2 + width

ax.bar(r1, np.array(outfr['abundance_count_per_m3']), color='steelblue', edgecolor='white', width=width, alpha=0.8,
       label='Outside Front')
ax.bar(r2, np.array(infr['abundance_count_per_m3']), color='mediumseagreen', edgecolor='white', width=width, alpha=0.8,
       label='Inside Front')
ax.bar(r3, np.array(marine['abundance_count_per_m3']), color='purple', edgecolor='white', width=width, alpha=0.8,
       label='Marine')

ax.set_xticks(r2 + width/3)
ax.set_xticklabels(outfr['species_display'], ha='right')
ax.set_ylabel(r'Zooplankton abundance (ind $\rm m^{-3}$)')  # \rm removes the italics
plt.xticks(fontsize=6, rotation=30)
plt.title('Fall 2019 Copepods')
plt.legend(fontsize=8)

plt_save = os.path.join(os.path.dirname(f), 'figures', 'zooplankton_abundance.png')
plt.savefig(str(plt_save), dpi=150)
plt.close

# need to break the y-axis for this figure
fig = plt.figure()
bax = brokenaxes(ylims=((0, 1500), (4000, 4500)), hspace=.1)

bax.bar(r1, np.array(outfr['abundance_count_per_m3']), color='steelblue', edgecolor='white', width=width, alpha=0.8,
        label='Outside Front')
bax.bar(r2, np.array(infr['abundance_count_per_m3']), color='mediumseagreen', edgecolor='white', width=width, alpha=0.8,
        label='Inside Front')
bax.bar(r3, np.array(marine['abundance_count_per_m3']), color='purple', edgecolor='white', width=width, alpha=0.8,
        label='Marine')

bax.axs[0].set_xticks([])
bax.axs[1].set_xticks(r2 + width/3)
bax.axs[1].set_xticklabels(outfr['species_display'], fontdict={'fontsize': 6}, rotation=30, ha='right')
bax.set_ylabel(r'Zooplankton abundance (ind $\rm m^{-3}$)')  # \rm removes the italics
bax.set_title('Fall 2019 Copepods')
bax.legend(fontsize=8, loc=2)

plt_save = os.path.join(os.path.dirname(f), 'figures', 'zooplankton_abundance_brokenaxis.png')
plt.savefig(str(plt_save), dpi=150)
plt.close

# bar chart with location on x-axis, inside and outside front only
width = 0.4

df_copes = df[(df['type'] != 'Other') & (df['station'] != 'marine')]
species = np.unique(df_copes['species_display']).tolist()
plt_ttl = 'Fall 2019 Copepods'
cols = cm.tab20(np.linspace(0, 1, len(species)))
stacked_bar_chart(df_copes, species, 'species_display', width, plt_ttl, 'zooplankton_abundance1.png', cols)

# bar chart with location on x-axis
df_copes = df[df['type'] != 'Other']
species = np.unique(df_copes['species_display']).tolist()
stacked_bar_chart(df_copes, species, 'species_display', width, plt_ttl, 'zooplankton_abundance2.png', cols)

# bar chart with location on x-axis, copepod groups
df_copes = df[df['type'] != 'Other']
df_copes_type = df_copes.groupby(['station', 'type']).sum().reset_index()
types = np.unique(df_copes['type']).tolist()
stacked_bar_chart(df_copes_type, types, 'type', width, plt_ttl, 'zooplankton_abundance3.png')

# bar chart with location on x-axis, A. tonsa only
df_atonsa = df[df['species_display'] == 'A. tonsa']
species = np.unique(df_atonsa['species_display']).tolist()
plt_ttl = 'Fall 2019 - Acartia tonsa'
stacked_bar_chart(df_atonsa, species, 'species_display', width, plt_ttl, 'zooplankton_abundance_atonsa.png')