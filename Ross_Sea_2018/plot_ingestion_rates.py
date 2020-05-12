#!/usr/bin/env python
"""
Created on May 11 2020 by Lori Garzio
@brief Creates box plots of zooplankton ingestion rates. The box limits extend from the lower to upper
quartiles, with a line at the median and a diamond symbol at the mean. Whiskers extend from the box to show the range
of the data.
f: file containing experimental data
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm
from statsmodels.formula.api import ols
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console


def main(f):
    df = pd.read_excel(f, sheet_name='forpython')
    spath = os.path.split(os.path.dirname(f))[0]

    type = ['Daily Individual Ingestion Rate', 'Community Ingestion Rate']
    for t in type:
        dft = df[['Experiment', t]]
        expts = np.unique(dft['Experiment']).tolist()
        bplot = []
        for expt in expts:
            dfi = dft.loc[df['Experiment'] == expt]
            ingestion_rates = dfi[t].tolist()
            bplot.append(ingestion_rates)
            mn = round(np.nanmean(ingestion_rates), 2)
            stdev = round(np.nanstd(ingestion_rates, ddof=1), 2)
            n = len(ingestion_rates)

            # test that data are normally distributed
            w, pvalue = stats.shapiro(ingestion_rates)
            if pvalue < .05:
                nd = 'No'
            else:
                nd = 'Yes'

            print('-------------')
            print(t)
            print('Experiment: {}'.format(expt))
            print('Ingestion rate (m/day)\n Avg = {} \n SD = {} \n n = {}'.format(mn, stdev, n))
            print('Data are normally distributed? {}'.format(nd))

            fig, ax = plt.subplots()
            try:
                ax.hist(dfi['Daily Individual Ingestion Rate'])
                xlab = 'Daily Individual Ingestion Rate \n({}g Chl-a equiv'.format(chr(956))
                ax.set_xlabel(' '.join((xlab, r'$\rm m^{-2} day^{-1}$)')))  # \rm removes the italics
                plt_fname = 'hist_ingestion_rate_individual_{}.png'.format(expt)
            except KeyError:
                ax.hist(dfi['Community Ingestion Rate'])
                xlab = 'Community Ingestion Rate \n({}g Chl-a equiv'.format(chr(956))
                ax.set_xlabel(' '.join((xlab, r'$\rm ind^{-2} day^{-1}$)')))  # \rm removes the italics
                plt_fname = 'hist_ingestion_rate_community_{}.png'.format(expt)
            plt.title('Histogram of ingestion rates: {}'.format(expt))
            ax.set_ylabel('Frequency')

            atext = AnchoredText('Shapiro-Wilk\nNormally distritubed? {}\np = {}'.format((nd), '{:.7f}'.format(pvalue)),
                                 loc='upper right', frameon=False, pad=1.5)
            ax.add_artist(atext)

            plt.tight_layout()
            plt_save = os.path.join(spath, 'figs', plt_fname)
            plt.savefig(str(plt_save), dpi=150)
            plt.close

        fig, ax = plt.subplots()

        # customize the boxplot elements
        medianprops = dict(color='black')
        meanpointprops = dict(marker='D', markeredgecolor='black', markerfacecolor='black')

        box = ax.boxplot(bplot, labels=expts, showmeans=True, medianprops=medianprops, meanprops=meanpointprops)
        ax.set_xlabel('Experiment')
        if 'Individual' in t:
            ylab = 'Daily Individual Ingestion Rate \n({}g Chl-a equiv'.format(chr(956))
            ax.set_ylabel(' '.join((ylab, r'$\rm m^{-2} day^{-1}$)')))  # \rm removes the italics
            plt_fname = 'ingestion_rate_individual.png'
        elif 'Community' in t:
            ylab = 'Community Ingestion Rate \n({}g Chl-a equiv'.format(chr(956))
            ax.set_ylabel(' '.join((ylab, r'$\rm ind^{-2} day^{-1}$)')))  # \rm removes the italics
            plt_fname = 'ingestion_rate_community.png'

        plt.tight_layout()
        plt_save = os.path.join(spath, 'figs', plt_fname)
        plt.savefig(str(plt_save), dpi=150)
        plt.close

        # calculate stats, from https://reneshbedre.github.io/blog/anova.html
        # pivot dataframe
        dft.insert(0, 'count', dft.groupby('Experiment').cumcount())
        dftp = dft.pivot(index='count', columns='Experiment', values=t)

        # one-way ANOVA
        fvalue, pvalue = stats.f_oneway(dftp['Expt1'], dftp['Expt2'], dftp['Expt3'], dftp['Expt4'])
        print('\n One-way ANOVA')
        print(fvalue, pvalue)

        # get ANOVA table as R like output
        dft.columns = ['count', 'treatments', 'value']
        model = ols('value ~ C(treatments)', data=dft).fit()  # Ordinary Least Squares (OLS) model
        anova_table = sm.stats.anova_lm(model, typ=2)
        print(anova_table)

        # multiple pair-wise comparison Tukey HSD
        m_comp = pairwise_tukeyhsd(endog=dft['value'], groups=dft['treatments'], alpha=0.05)
        print('\nTukey HSD pairwise-comparison')
        print(m_comp)

        # Shapiro-Wilk to test normal distribution of residuals
        w, sw_pvalue = stats.shapiro(model.resid)
        print('\nShapiro-Wilk test for normal distribution of residuals')
        print(w, sw_pvalue)

        if sw_pvalue < .05:
            nd = 'No'
            print('Residuals are not normally distributed')
        else:
            nd = 'Yes'
            print('Residuals are normally distributed')

        fig, ax = plt.subplots()
        ax.hist(dft['value'])
        if 'Individual' in t:
            xlab = 'Daily Individual Ingestion Rate \n({}g Chl-a equiv'.format(chr(956))
            ax.set_xlabel(' '.join((xlab, r'$\rm m^{-2} day^{-1}$)')))  # \rm removes the italics
            plt_fname = 'hist_ingestion_rate_individual_allexpts.png'
        else:
            xlab = 'Community Ingestion Rate \n({}g Chl-a equiv'.format(chr(956))
            ax.set_xlabel(' '.join((xlab, r'$\rm ind^{-2} day^{-1}$)')))  # \rm removes the italics
            plt_fname = 'hist_ingestion_rate_community_allexpts.png'
        plt.title('Histogram of ingestion rates')
        ax.set_ylabel('Frequency')

        atext = AnchoredText('Shapiro-Wilk\nNormally distritubed? {}\np = {}'.format((nd), '{:.7f}'.format(sw_pvalue)),
                             loc='upper right', frameon=False, pad=1.5)
        ax.add_artist(atext)

        plt.tight_layout()
        plt_save = os.path.join(spath, 'figs', plt_fname)
        plt.savefig(str(plt_save), dpi=150)
        plt.close


if __name__ == '__main__':
    fname = '/Users/lgarzio/Documents/rucool/Saba/Ross_Sea/Ross_Sea2018_grazing/data/Krill_grazing_stats.xlsx'
    main(fname)
