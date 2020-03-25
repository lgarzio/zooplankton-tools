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
from brokenaxes import brokenaxes
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

f = '/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_zooplankton_abundance.xlsx'

df = pd.read_excel(f, sheet_name='abundance')
df['species_display'] = ''

for i, row in df.iterrows():
    # shorten copepod species names
    if 'Copepod' in row['type']:
        df.loc[i, 'species_display'] = '. '.join((row['species'].split(' ')[0][0], row['species'].split(' ')[1]))
    else:
        df.loc[i, 'species_display'] = row['species']

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
bax = brokenaxes(ylims=((0, 400), (1000, 1100)), hspace=.1)

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
