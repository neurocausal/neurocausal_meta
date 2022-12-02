"""
Author: mesparza
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

import pandas as pd

import seaborn as sns

# %%
df = pd.read_csv("/home/mesparza/data/brainhack_donosti/out_exclude_35.csv")
# sns.regplot(df, x='exclusion_perc', y='clinical_perc',
#             scatter_kws={'alpha': 0.5}, line_kws={'color':'k'})
# plt.show()
ex = 4
cl = 2
df_filtered = df.query('exclusion_perc < 4 & clinical_perc > 2')
text = df_filtered.describe().loc['count'][0]/df.describe().loc['count'][0]*100
text = np.round(text,3)

with plt.style.context('classic'):
    # sns.set(rc={'figure.facecolor': 'white'})
    sns.set_context("talk")
    fig = sns.jointplot(data=df, x='exclusion_perc', y='clinical_perc',
                        kind='reg',
                        joint_kws={
                            'scatter_kws': {'alpha': 0.5, 'color': 'b'},
                            'line_kws': {'color': 'k'}})
    fig.fig.patch.set_facecolor('white')
    # fig.fig.axes[0].axvline(x=ex, color='r')
    # fig.fig.axes[0].axhline(y=cl, color='r')
    # fig.fig.axes[0].text(5, 10.5, s=str(text)+' %', color='r')
    # fig.fig.axes[0].add_patch(Rectangle((0, cl), ex, 12, color="r", alpha=0.3))
    fig.fig.axes[0].set_xlabel('Exclusion word percentage')
    fig.fig.axes[0].set_ylabel('Clinical word percentage')
    sns.set(font="Arial")
    plt.show()


