import os

import pandas as pds
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


def log_map(x, root=10):
    if root == 10:
        return 20 * np.log10(x)
    elif root == 2:
        return 20 * np.log2(x)
    else:
        return 20 * np.log(x)


if __name__ == "__main__":
    start = '2023/10/1'
    end = '2024/4/1'
    gold_price = pds.read_csv("gold_price.csv")
    bit_price = pds.read_csv("bitcoin_price.csv")
    total_df = gold_price.join(bit_price.set_index('date'),
                               on='date', how='left')
    total_df.price /= 20
    total_df = total_df.rename(columns={'price': 'gold_price'})
    total_df.bitcoin_price = total_df.bitcoin_price.map(lambda x: log_map(x, 10))
    # total_df.price = total_df.price.map(lambda x: log_map(x, 2))
    total_df.set_index('date')

    trend_df = pds.DataFrame()
    for file in os.listdir("trend"):
        # print(trend_df.head())
        fp = os.path.join('trend', file)
        f = pds.read_csv(fp, encoding='gbk')
        # f.set_index('月份')
        if not len(trend_df):
            trend_df = f
        else:
            trend_df = trend_df.join(f.set_index('月份'),on='月份',how='left')
    trend_df.columns = [x.split(": ")[0] for x in trend_df.columns]
    for col in trend_df.columns[1:]:
        trend_df[col] = trend_df[col] - trend_df[col].min()
        trend_df[col] = trend_df[col] / trend_df[col].max()
    war_cols = ['world war','Middle East','nuclear weapon','Russia Ukraine']
    polical_cols = ['china', 'taiwan', 'election']
    disease_cols = ['covid','epidemic']
    other_cols = ['Climate deterioration']
    # trend_df = trend_df[['月份']+other_cols]
    use_cols = ['Middle East','Russia Ukraine','china', 'taiwan', 'election',
                'covid']
    trend_df = trend_df[['月份'] + use_cols]
    trend_df['merge_trend']= trend_df.iloc[:,1:].sum(axis=1)
    trend_df = trend_df[['月份','merge_trend']]

    total_df = total_df.join(trend_df.set_index('月份'),
                             on='date',how='left')
    prev = 0
    def trend_fillna(x):
        global prev
        if pds.isnull(x):
            return prev
        else:
            prev = x
            return x
    total_df['merge_trend'] = total_df['merge_trend'].map(trend_fillna)

    # ax = plt.subplot(211)
    # trend_df.plot(ax=ax)
    # ax.set_xticks(range(len(trend_df)))
    # ax.set_xticklabels(trend_df['月份'],
    #                    rotation=90, fontsize=6)
    # ax1 = plt.subplot(212)
    # total_df.plot(ax=ax1)
    # # ax1.set_xticks(range(len(total_df)))
    # ax1.set_xticklabels(total_df['date'],
    #                     rotation=90, fontsize=6)
    start_date = datetime.strptime(start, '%Y/%m/%d')
    end_date = datetime.strptime(end, '%Y/%m/%d')
    total_df.date = total_df.date.map(lambda x: datetime.strptime(x, '%Y/%m/%d'))
    total_df = total_df[(total_df.date >= start_date)&(total_df.date < end_date)]
    total_df.date = total_df.date.map(lambda x: datetime.strftime(x, '%Y/%m/%d'))

    print(total_df.head())
    print(total_df.iloc[:, 1:].corr())

    total_df['merge_trend'] = total_df['merge_trend'] * 20
    total_df.reset_index(drop=True).plot()
    plt.xticks(range(len(total_df)),total_df.date.values,
               rotation=90,fontsize=6)
    plt.legend()
    plt.grid(axis='x')
    plt.show()
