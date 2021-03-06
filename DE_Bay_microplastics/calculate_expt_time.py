#!/usr/bin/env python
"""
Created on Jan 30 2020 by Lori Garzio
@brief Calculate experiment time in hours and add to the input csv file as a column
f: file containing experiment start and end times
expt: experiment to analyze (options: expt1, expt2)
"""

import datetime as dt
import pandas as pd
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

expt = 'expt1'  # expt1 or expt2
f = ''.join(('/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_', expt, '.xlsx'))
csv_file = ''.join(('/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_', expt, '_temp.csv'))

df = pd.read_excel(f, sheet_name='expt_data')

df['t0mod'] = df['t0'].map(lambda t: dt.datetime.strptime(t, '%Y-%m-%dT%H:%M'))
df['tfmod'] = df['tf'].map(lambda t: dt.datetime.strptime(t, '%Y-%m-%dT%H:%M'))
df['expt_time_hours'] = df['tfmod'] - df['t0mod']

# convert timedelta to seconds, then hours
df['expt_time_hours'] = df['expt_time_hours'].map(lambda ts: ts.total_seconds()/60/60)

df.drop(columns=['t0mod', 'tfmod'], inplace=True)
df.to_csv(csv_file, index=False)
