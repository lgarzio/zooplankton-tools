#!/usr/bin/env python
"""
Created on Apr 16 2020 by Lori Garzio
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
        bar_data = np.array(sdf['abundance_count_per_m3'])
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
    ax.set_ylabel(r'Abundance (ind $\rm m^{-2}$)')  # \rm removes the italics
    plt.ylim([0, 1950])
    #plt.title(plot_title)
    #plt.legend(fontsize=8)
    if len(r) == 2:
        plt.subplots_adjust(top=0.9, right=0.6)
        legend_x = np.max(ax.get_xlim()) * .8
    elif len(r) == 3:
        plt.subplots_adjust(top=0.9, right=0.69)
        legend_x = np.max(ax.get_xlim()) * .45
    else:
        plt.subplots_adjust(top=0.9, right=0.7)
        legend_x = np.max(ax.get_xlim()) * .24

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc=(legend_x, 0.4), fontsize=8, frameon=False)
    plt.tight_layout()

    plt_save = os.path.join(fpath, 'zooplankton_figs', sname)
    plt.savefig(str(plt_save), dpi=150)
    plt.close


def main(f):
    # plots by time period
    df = pd.read_excel(f, sheet_name='abundance')
    df = df.melt(id_vars='Tow', var_name='Species', value_name='abundance_count_per_m3')
    df_key = pd.read_excel(f, sheet_name='key')
    df = pd.merge(df, df_key, on=['Tow'], how='outer')
    #df.sort_values(by=['Tow'], inplace=True)  # make sure the dataframe is sorted

    time_pds = [x for x in np.unique(df['Period']) if 'no_period' not in x]

    species = ['E. crystallorophias adult', 'E. crystallorophias juveniles', 'T. macrura', 'Copepods',
               'Amphipods', 'Pteropods', 'P. antarctica adult/juvenile', 'P. antarctica larvae']
    cols = ['red', 'firebrick', 'darkorange', 'xkcd:maize', 'darkgreen', 'steelblue', 'indigo', 'gray']

    for tp in time_pds:
        df_tp = df[df['Period'] == tp]

        # plot all tows per time period
        #species = np.unique(df_tp['Species']).tolist()
        #cols = cm.tab20(np.linspace(0, 1, len(species)))
        #cols = cm.rainbow(np.linspace(0, 1, len(species)))

        stacked_bar_chart(df_tp, species, 'Species', '_'.join((tp, 'zoop_abundance.png')), os.path.dirname(f), cols)

        # plot only the tows for biomass comparison
        df_tp_bc = df_tp[df_tp['Comparison'] == 'yes']
        stacked_bar_chart(df_tp_bc, species, 'Species', '_'.join((tp, 'zoop_abundance_biomasscompare.png')),
                          os.path.dirname(f), cols)


if __name__ == '__main__':
    fname = '/Users/lgarzio/Documents/rucool/Saba/Ross_Sea/Ross_Sea2018/zooplankton_abundance_subset_CORRECTED_ind_m2.xlsx'
    main(fname)
