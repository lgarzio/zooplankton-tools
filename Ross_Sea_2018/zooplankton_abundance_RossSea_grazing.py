#!/usr/bin/env python
"""
Created on May 11 2020 by Lori Garzio
@brief Creates a bar chart of zooplankton abundance
fname: file containing zooplankton abundance data
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
pd.set_option('display.width', 320, "display.max_columns", 15)  # for display in pycharm console


def stacked_bar_chart(dataframe, group_list, column_name, sname, fpath, colors=None):
    fig, ax = plt.subplots()
    if len(np.unique(dataframe['Tow'])) > 3:
        bar_width = 0.6
    else:
        bar_width = 0.5

    for ind in range(len(group_list)):
        sdf = dataframe[dataframe[column_name] == group_list[ind]]
        try:
            bar_data = np.array(sdf['abundance_count_per_m3'])
            ylab = r'Abundance (ind $\rm m^{-3}$)'  # \rm removes the italics
        except KeyError:
            bar_data = np.array(sdf['percent_abundance'])
            ylab = 'Percent Abundance (%)'
        alpha = .8

        if ind == 0:
            r = np.arange(len(sdf))
            if colors is not None:
                ax.bar(r, bar_data, width=bar_width, color=colors[ind], edgecolor='black', label=group_list[ind],
                       alpha=alpha)
            else:
                ax.bar(r, bar_data, width=bar_width, edgecolor='black', label=group_list[ind], alpha=alpha)
            bottoms = bar_data
        else:
            if colors is not None:
                ax.bar(r, bar_data, width=bar_width, bottom=bottoms, color=colors[ind], edgecolor='black',
                       label=group_list[ind], alpha=alpha)
            else:
                ax.bar(r, bar_data, width=bar_width, bottom=bottoms, edgecolor='black', label=group_list[ind],
                       alpha=alpha)
            bottoms = bottoms + bar_data

    ax.set_xticks(r)
    ax.set_xticklabels(sdf['Tow'].tolist())
    ax.set_ylabel(ylab)

    # adjust plot limits
    plt.subplots_adjust(top=0.9, right=0.6)
    legend_x = np.max(ax.get_xlim()) * .3

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc=(legend_x, 0.4), fontsize=8, frameon=False)  # reverse legend display
    plt.tight_layout()

    plt_save = os.path.join(fpath, 'figs', sname)
    plt.savefig(str(plt_save), dpi=150)
    plt.close


def main(f):
    # plots by time period
    spath = os.path.split(os.path.dirname(f))[0]
    sheets = ['abundance', 'percent_abundance']
    for sh in sheets:
        df = pd.read_excel(f, sheet_name=sh)
        if sh == 'abundance':
            colname = 'abundance_count_per_m3'
        elif sh == 'percent_abundance':
            colname = 'percent_abundance'
        df = df.melt(id_vars='Tow', var_name='Species', value_name=colname)

        species = ['E. crystallorophias adult', 'T. macrura', 'Amphipods', 'Pteropods', 'P. antarctica adult/juvenile',
                   'P. antarctica larvae']
        cols = ['firebrick', 'darkorange', 'darkgreen', 'steelblue', 'indigo', 'gray']

        stacked_bar_chart(df, species, 'Species', 'zoop_{}.png'.format(sh), spath, cols)


if __name__ == '__main__':
    fname = '/Users/lgarzio/Documents/rucool/Saba/Ross_Sea/Ross_Sea2018_grazing/data/zooplankton_abundance_grazing_subset_CORRECTED.xlsx'
    main(fname)
