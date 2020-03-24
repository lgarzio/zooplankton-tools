#!/usr/bin/env python
"""
Created on Mar 24 2020 by Lori Garzio
@brief Creates box plots of zooplankton fecal pellet sinking rates. The box limits extend from the lower to upper
quartiles, with a line at the median and a diamond symbol at the mean. Whiskers extend from the box to show the range
of the data.
expt: experiment to analyze (options: expt1, expt2)
f: file containing fecal pellet sinking rates
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from scipy import stats
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

expt = 'expt2'  # expt1 or expt2
f = ''.join(('/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_', expt, '_FP.xlsx'))

df = pd.read_excel(f)

cruises = np.unique(df['cruise']).tolist()
bplot = []
labs = []
for cruise in cruises:
    dfc = df.loc[df['cruise'] == cruise]
    stations = np.unique(dfc['station']).tolist()
    for sta in stations:
        if sta == 'inside_front':
            labs.append('Inside Front')
        elif sta == 'outside_front':
            labs.append('Outside Front')
        elif sta == 'algae':
            labs.append('Algae Only')
        elif sta == 'algae_plastic':
            labs.append('Algae + Plastic')
        else:
            labs.append(sta)
        dfi = dfc.loc[df['station'] == sta]
        sinking_rates = dfi['sinking_rate_m_day'].tolist()
        bplot.append(sinking_rates)
        mn = round(np.nanmean(sinking_rates), 2)
        stdev = round(np.nanstd(sinking_rates, ddof=1), 2)
        n = len(sinking_rates)
        print('-------------')
        print('Treatment: {}'.format(sta))
        print('Sinking rates (m/day)\n Avg = {} \n SD = {} \n n = {}'.format(mn, stdev, n))
    fig, ax = plt.subplots()
    if expt == 'expt1':
        colors = ['darkgray', 'steelblue']
    else:
        colors = ['darkgray', 'seagreen']

    # customize the boxplot elements
    medianprops = dict(color='black')
    meanpointprops = dict(marker='D', markeredgecolor='black', markerfacecolor='black')

    box = ax.boxplot(bplot, patch_artist=True, labels=labs, showmeans=True, medianprops=medianprops,
                     meanprops=meanpointprops)

    # change the colors of the boxes
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    ax.set_xlabel('Treatment')
    ax.set_ylabel(r'FP sinking rate (m $\rm day^{-1}$)')  # \rm removes the italics
    plt.title('Fall 2019')

    # calculate Student's t-test
    t2, p2 = stats.ttest_ind(bplot[0], bplot[1])
    atext = AnchoredText('t = {}\np = {}'.format(abs(round(t2, 2)), round(p2, 4)), loc=1, frameon=False, pad=1.5)
    ax.add_artist(atext)

    plt_fname = ''.join(('FP_sinking_rates_', expt, '.png'))
    plt_save = os.path.join(os.path.dirname(f), 'figures', plt_fname)
    plt.savefig(str(plt_save), dpi=150)
    plt.close
