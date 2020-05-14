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
plt.rcParams['font.family'] = 'Times'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams.update({'font.size': 16})
pd.set_option('display.width', 320, "display.max_columns", 15)  # for display in pycharm console


def stacked_bar_chart(dataframe, group_list, column_name, sname, fpath, colors=None):
    fig, ax = plt.subplots()
    bar_width = 0.8

    for ind in range(len(group_list)):
        sdf = dataframe[dataframe[column_name] == group_list[ind]]
        bar_data = np.array(sdf['percent_abundance'])
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
    ax.set_ylabel('Percent Abundance (%)')

    # adjust plot limits
    plt.subplots_adjust(top=0.9, right=0.6)
    legend_x = np.max(ax.get_xlim()) * .3

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc=(legend_x, 0.35), fontsize=10, frameon=False)  # reverse legend display
    plt.tight_layout()

    plt_save = os.path.join(fpath, 'figs', sname)
    plt.savefig(str(plt_save), dpi=150)
    plt.close


def main(f):
    # plots by time period
    spath = os.path.split(os.path.dirname(f))[0]
    sheets = ['percent_abundance', 'abundance_ind_m2']
    for sh in sheets:
        df = pd.read_excel(f, sheet_name=sh)
        if sh == 'abundance_ind_m2':
            fig, ax = plt.subplots()
            ax.bar(df['Tow'], df['Total'], color='k')
            ax.set_ylabel(r'Total Zooplankton Abundance (ind $\rm m^{-2}$)')  # \rm removes the italics'

            plt_save = os.path.join(spath, 'figs', 'zoop_abundance_total.png')
            plt.savefig(str(plt_save), dpi=150)
            plt.close

        elif sh == 'percent_abundance':
            colname = 'percent_abundance'
            df = df.melt(id_vars='Tow', var_name='Species', value_name=colname)

            species = ['E. crystallorophias adult', 'T. macrura', 'Amphipods', 'Pteropods', 'P. antarctica adult/juvenile',
                       'P. antarctica larvae', 'Other rare']
            cols = ['forestgreen', 'firebrick', 'cornflowerblue', 'orange', 'blue', 'xkcd:warm purple', 'xkcd:sun yellow']

            stacked_bar_chart(df, species, 'Species', 'zoop_{}.png'.format(sh), spath, cols)


if __name__ == '__main__':
    fname = '/Users/lgarzio/Documents/rucool/Saba/Ross_Sea/Ross_Sea2018_grazing/data/zooplankton_abundance_grazing_forpython.xlsx'
    main(fname)
