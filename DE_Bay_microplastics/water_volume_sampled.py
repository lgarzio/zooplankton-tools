#!/usr/bin/env python
"""
Created on Jan 30 2020 by Lori Garzio
@brief Calculate the volume of water sampled by a zooplankton net and add to the input csv file as a column
rotor_constant: rotor constant specific to the flowmeter
r: radius of net opening in meters
csv_file: file containing flowmeter readings
"""

import pandas as pd
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console

rotor_constant = 26873  # rotor constant specific to the flowmeter
r = 0.25  # radius of net opening in meters (half meter ring net)
csv_file = '/Users/lgarzio/Documents/rucool/Saba/microplastics/NOAA2018/data/DEBay_MP_fieldsampling.csv'


df = pd.read_csv(csv_file)

df['flowmeter_diff'] = df['flowmeter_end'] - df['flowmeter_start']

# (distance m) * (area of net opening m3)
df['vol_sampled_m3'] = (df['flowmeter_diff'] * rotor_constant / 999999) * (3.14 * r * r)
df.to_csv(csv_file, index=False)
