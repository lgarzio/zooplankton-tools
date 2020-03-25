#!/usr/bin/env python
"""
Created on Feb 5 2020 by Lori Garzio
@brief Calculate zooplankton ingestion rates using experimental data
expt: experiment to analyze (options: expt1, expt2)
f: file containing experimental data; chl-a data at initial and final time points
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from scipy import stats
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

expt = 'expt1'  # expt1 or expt2
f = ''.join(('/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_', expt, '.xlsx'))
sname = '_'.join(('DEBay_MP', expt, 'chla_ingest_rates_summary'))


# headers for final output
sheaders = ['cruise', 'treatment', 'full_treatment', 'chl_t0', 'chl_tf', 'time_hours',
            'clearance_rate (mls/individual/hour)', 'ingestion_rate (ug Chl/ind/hr)', 'ingestion_rate (ug Chl/ind/day)']

summary = []

df = pd.read_excel(f, sheet_name='chla')
hours_df = pd.read_excel(f, sheet_name='expt_data')
df['btl_tp'] = df['Bottle'] + '_' + df['Time Point']
cruises = np.unique(df['Cruise']).tolist()
for cruise in cruises:
    dfc = df.loc[df['Cruise'] == cruise]
    try:
        stations = np.unique(dfc['Station']).tolist()
        sta_header = 'Station'
    except KeyError:
        stations = np.unique(dfc['Treatment']).tolist()
        sta_header = 'Treatment'
    if stations == ['inside_front', 'outside_front']:
        stations = ['outside_front', 'inside_front']
    for sta in stations:
        dfi = dfc.loc[df[sta_header] == sta]

        # calculate average chl-a for the controls at each time point
        controls = dfi[dfi['btl_tp'].str.contains('control')]
        timepts = np.unique(controls['Time Point']).tolist()
        for tps in timepts:
            if 't0' in tps or 'T0' in tps:
                c_avg_t0 = np.average(controls[controls['Time Point'] == tps]['Chl (ug/l)'])
            elif 'tf' in tps or 'Tf' in tps:
                c_avg_tf = np.average(controls[controls['Time Point'] == tps]['Chl (ug/l)'])

        # calculate the average experiment time for the controls
        try:
            c_expt_time = np.average(hours_df.loc[(hours_df['cruise'] == cruise) &
                                                  (hours_df['station'] == sta) &
                                                  (hours_df['bottle'].str.contains('control'))]['expt_time_hours'])
        except KeyError:
            c_expt_time = np.average(hours_df.loc[(hours_df['cruise'] == cruise) &
                                                  (hours_df['treatment'] == sta) &
                                                  (hours_df['bottle'].str.contains('control'))]['expt_time_hours'])

        summary.append([cruise, sta, '_'.join((sta, 'control_avg')), c_avg_t0, c_avg_tf, c_expt_time])

        # calculate k from the controls
        k = (np.log(c_avg_tf / c_avg_t0)) / c_expt_time

        # add the treatment data to the summary
        treatments = dfi[dfi['btl_tp'].str.contains('treatment')]
        for i, row in treatments.iterrows():
            try:
                hours_df['station']
                hours_header = 'station'
            except KeyError:
                hours_header = 'treatment'

            tmt_time_row = hours_df.loc[(hours_df['cruise'] == cruise) &
                                        (hours_df[hours_header] == sta) &
                                        (hours_df['bottle'] == row['Bottle'])]
            tmt_time_array = np.array(tmt_time_row['expt_time_hours'])
            if len(tmt_time_array) == 1:
                tmt_time = tmt_time_array[0]
            else:
                raise ValueError('Check experiment times: {} {} {}'.format(cruise, sta, row['Bottle']))

            neg_g_prime = np.log(row['Chl (ug/l)'] / c_avg_t0) / tmt_time
            g = -neg_g_prime + k
            clearance_rate = row['expt_vol_ml'] * g / row['num_copes']  # clearance rate, mls/individual/hour
            c = ((c_avg_t0 * ((np.exp(neg_g_prime * tmt_time)) - 1)) / (neg_g_prime * tmt_time)) / 1000  # ug/ml
            ingest_rate_hour = clearance_rate * c  # ug Chl/ind/hour
            ingest_rate_day = ingest_rate_hour * 24  # ug Chl/ind/day

            summary.append([cruise, row[sta_header], '_'.join((sta, row['Bottle'])), c_avg_t0, row['Chl (ug/l)'],
                            tmt_time, clearance_rate, ingest_rate_hour, ingest_rate_day])


summary_df = pd.DataFrame(summary, columns=sheaders)

summary.append([])  # add extra blank row
summary.append(['cruise', 'treatment', 'ingestion_rate_avg (ug Chl/ind/day)', 'ingestion_rate_stdev (ug Chl/ind/day)'])

# calculate averages and stdev for each treatment
plotting_df = pd.DataFrame()
stats_dict = dict()
for cruise in cruises:
    plotting_dict = dict(cruise=[], labels=[], ingestion_rates=[], stdev=[])
    sdfc = summary_df.loc[summary_df['cruise'] == cruise]
    try:
        stats_dict[cruise]
    except KeyError:
        stats_dict[cruise] = dict()
    for sta in stations:
        sdfi = sdfc.loc[sdfc['treatment'] == sta]
        ir = np.array(sdfi['ingestion_rate (ug Chl/ind/day)'])
        ir = ir[~np.isnan(ir)]
        ir[ir < 0] = 0  # set negative ingestion rates to zero
        stats_dict[cruise][sta] = ir
        mn = np.nanmean(ir)
        stdev = np.nanstd(ir, ddof=1)
        summary.append([cruise, sta, mn, stdev])
        plotting_dict['cruise'].append(cruise)
        if sta == 'inside_front':
            plotting_dict['labels'].append('Inside Front')
        elif sta == 'outside_front':
            plotting_dict['labels'].append('Outside Front')
        elif sta == 'algae':
            plotting_dict['labels'].append('Algal Culture')
        elif sta == 'algae_plastic':
            plotting_dict['labels'].append('Algal Culture + Plastic')
        else:
            plotting_dict['labels'].append(sta)
        plotting_dict['ingestion_rates'].append(mn)
        plotting_dict['stdev'].append(stdev)
    df = pd.DataFrame(plotting_dict)
    if len(plotting_df) < 1:
        plotting_df = df
    else:
        plotting_df = plotting_df.append(df, ignore_index=True)

fig, ax = plt.subplots()
if expt == 'expt1':
    c = 'steelblue'
else:
    c = 'seagreen'
ax.bar(plotting_df['labels'], plotting_df['ingestion_rates'], color=c, label='Fall2019', yerr=plotting_df['stdev'], capsize=8)

#### for more than 1 cruise
# colors = ['firebrick', 'mediumseagreen', 'purple']
# width = 0.25
# fall = plotting_df[plotting_df['cruise'] == 'Fall2019']
# spring = plotting_df[plotting_df['cruise'] == 'Spring2020']
#
# ind = np.arange(len(fall))
#
# rects1 = ax.bar(ind, np.array(fall['ingestion_rates']), color='firebrick', width=width, alpha=0.5,
#                 label='Fall2019', yerr=fall['stdev'], capsize=8)
# rects2 = ax.bar(ind + width, np.array(spring['ingestion_rates']), color='blue', width=width, alpha=0.5,
#                 label='Spring2020', yerr=spring['stdev'], capsize=8)
# ax.set_xticks(ind + width/2)
# ax.set_xticklabels(fall['labels'])

#ax.legend(loc='best')
ax.set_xlabel('Treatment')
ylab = 'Ingestion Rates ({}g Chl'.format(chr(956))
ax.set_ylabel(' '.join((ylab, r'$\rm ind^{-1} day^{-1}$)')))  # \rm removes the italics
plt.title('Fall 2019')

# calculate Student's t-test
try:
    t2, p2 = stats.ttest_ind(stats_dict['Fall2019']['inside_front'], stats_dict['Fall2019']['outside_front'])
    atext = AnchoredText('t = {}\np = {}'.format(abs(round(t2, 2)), round(p2, 3)), loc=1, frameon=False, pad=1.5)
except KeyError:
    t2, p2 = stats.ttest_ind(stats_dict['Fall2019']['algae'], stats_dict['Fall2019']['algae_plastic'])
    atext = AnchoredText('t = {}\np = {}'.format(abs(round(t2, 2)), round(p2, 4)), loc=1, frameon=False, pad=1.5)

ax.add_artist(atext)

plt_fname = ''.join(('Chla_ingest_rates_', expt, '.png'))
plt_save = os.path.join(os.path.dirname(f), 'figures', plt_fname)
plt.savefig(str(plt_save), dpi=150)
plt.close

summary_df = pd.DataFrame(summary, columns=sheaders)
summary_df.to_csv('{}/{}.csv'.format(os.path.dirname(f), sname), index=False)
