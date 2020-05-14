#!/usr/bin/env python
"""
Created on May 14 2020 by Lori Garzio
@brief Calculate stats for krill lengths from grazing experiments
f: file containing experimental data
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import itertools
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console


def rank_transformation(data):
    rd = stats.rankdata(data)
    p = rd / (len(rd) + 1)
    d_trans = stats.norm.ppf(p, 0, 1)
    return d_trans


def main(f):
    df = pd.read_excel(f, sheet_name='krill_length')
    spath = os.path.split(os.path.dirname(f))[0]

    # check normality
    data = []
    for col in df.columns:
        d = df[col].dropna()
        data.append(d)

        # rank transformation
        d_transformed = rank_transformation(d)

        # test that data are normally distributed
        w, pvalue = stats.shapiro(d_transformed)
        if pvalue < .05:
            nd = 'No'
        else:
            nd = 'Yes'

        fig, ax = plt.subplots()
        ax.hist(d_transformed)
        ax.set_xlabel('Rank Transformed Krill Length')

        atext = AnchoredText('Shapiro-Wilk\nNormally distritubed? {}\np = {}'.format((nd), '{:.7f}'.format(pvalue)),
                             loc='upper right', frameon=False, pad=1.5)

        ax.add_artist(atext)
        plt.tight_layout()

        plt_fname = 'hist_krill_length_{}_ranktransformed.png'.format(col)
        plt_save = os.path.join(spath, 'figs', 'krill_length', plt_fname)
        plt.savefig(str(plt_save), dpi=150)
        plt.close

    # plot all data
    data2 = list(itertools.chain(*data))
    data_transformed = rank_transformation(data2)
    fig, ax = plt.subplots()
    ax.hist(data_transformed)
    ax.set_xlabel('Rank Transformed Krill Length')

    atext = AnchoredText('Shapiro-Wilk\nNormally distritubed? {}\np = {}'.format((nd), '{:.7f}'.format(pvalue)),
                         loc='upper right', frameon=False, pad=1.5)

    ax.add_artist(atext)
    plt.tight_layout()

    plt_fname = 'hist_krill_length_ranktransformed.png'
    plt_save = os.path.join(spath, 'figs', 'krill_length', plt_fname)
    plt.savefig(str(plt_save), dpi=150)
    plt.close

    # pivot the dataframe to do the rank transformation
    dft = pd.melt(df.reset_index(), id_vars=['index'], value_vars=df.columns.tolist())
    dft = dft.dropna()
    dft.columns = ['count', 'treatments', 'value']
    dft['value_rt'] = rank_transformation(dft['value'])

    # pivot dataframe again, only keeping the transformed data
    dftp = dft.pivot(index='count', columns='treatments', values='value_rt')

    # one-way ANOVA, from https://reneshbedre.github.io/blog/anova.html
    fvalue, pvalue = stats.f_oneway(dftp['Expt1'].dropna(), dftp['Expt2'].dropna(), dftp['Expt3'].dropna(), dftp['Expt4'].dropna())
    print('\n One-way ANOVA')
    print(fvalue, pvalue)

    # get ANOVA table as R like output
    model = ols('value_rt ~ C(treatments)', data=dft).fit()  # Ordinary Least Squares (OLS) model
    anova_table = sm.stats.anova_lm(model, typ=2)
    print(anova_table)

    # multiple pair-wise comparison Tukey HSD
    m_comp = pairwise_tukeyhsd(endog=dft['value_rt'], groups=dft['treatments'], alpha=0.05)
    print('\nTukey HSD pairwise-comparison')
    print(m_comp)

    # Shapiro-Wilk to test normal distribution of residuals
    w, sw_pvalue = stats.shapiro(model.resid)
    print('\nShapiro-Wilk test for normal distribution of residuals')
    print(w, sw_pvalue)

    if sw_pvalue < .05:
        print('Residuals are not normally distributed')
    else:
        print('Residuals are normally distributed')


if __name__ == '__main__':
    fname = '/Users/lgarzio/Documents/rucool/Saba/Ross_Sea/Ross_Sea2018_grazing/data/Krill_grazing_stats.xlsx'
    main(fname)
