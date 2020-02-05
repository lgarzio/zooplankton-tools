#!/usr/bin/env python
"""
Created on Feb 5 2020 by Lori Garzio
@brief Calculate zooplankton ingestion rates using experimental data
volume_ml: experimental bottle volume in milliliters
n: number of individual zooplankton in experimental bottles
f: file containing chl-a data at initial and final time points
f_hours: file containing the experimental time elapsed for each treatment
sname: name assignment for the output file
"""

import numpy as np
import pandas as pd
import os
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

volume_ml = 800  # experimental bottle volume in mls
n = 48  # number of individual zooplankton in experimental bottles
f = '/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_expt1_chla1.xlsx'
f_hours = '/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_expt1.csv'
sname = 'DEBay_MP_expt1_ingest_rates'


# headers for final output
sheaders = ['cruise', 'treatment', 'full_treatment', 'chl_t0', 'chl_tf', 'time_hours',
            'clearance_rate (mls/individual/hour)', 'ingestion_rate (ug Chl/ind/hr)', 'ingestion_rate (ug Chl/ind/day)']

summary = []

df = pd.read_excel(f)
hours_df = pd.read_csv(f_hours)
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

        # calculate k
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
            clearance_rate = volume_ml * g / n  # clearance rate, mls/individual/hour
            c = ((c_avg_t0 * ((np.exp(neg_g_prime * tmt_time)) - 1)) / (neg_g_prime * tmt_time)) / 1000  # ug/ml
            ingest_rate_hour = clearance_rate * c  # ug Chl/ind/hour
            ingest_rate_day = ingest_rate_hour * 24  # ug Chl/ind/day

            summary.append([cruise, row[sta_header], '_'.join((sta, row['Bottle'])), c_avg_t0, row['Chl (ug/l)'],
                            tmt_time, clearance_rate, ingest_rate_hour, ingest_rate_day])


summary_df = pd.DataFrame(summary, columns=sheaders)

summary.append([])  # add extra blank row
summary.append(['cruise', 'treatment', 'ingestion_rate_avg (ug Chl/ind/day)', 'ingestion_rate_stdev (ug Chl/ind/day)'])

# calculate averages
for cruise in cruises:
    sdfc = summary_df.loc[summary_df['cruise'] == cruise]
    for sta in stations:
        sdfi = sdfc.loc[sdfc['treatment'] == sta]
        ir = np.array(sdfi['ingestion_rate (ug Chl/ind/day)'])
        ir[ir < 0] = 0  # set negative ingestion rates to zero
        mn = np.nanmean(ir)
        stdev = np.nanstd(ir, ddof=1)
        summary.append([cruise, sta, mn, stdev])

summary_df = pd.DataFrame(summary, columns=sheaders)
summary_df.to_csv('{}/{}.csv'.format(os.path.dirname(f), sname), index=False)
