import os
import copy
import sys
import random
import gc
import datetime
import subprocess
import pickle
import pandas as pd


if __name__ == '__main__':
    models = [
        # 'CTCDPoi',
        # 'CTCDBer',
        # 'COLDSlice',
        'COLD',
    ]
    datasets = [
        'MIXED_200', #19 290
        # 'AAAI',
        # 'SIGCOMM',
        # 'dblp_citation',
        # 'dblp_coauthor',
        # 'weibo',
    ]
    community_count = [
        19,
        290,
        # 287,
        # 265,
        # 10,
        # 50,
        # 100,
        # 150,
    ]
    predict_modes = [
        # 'top',
        'nlog'
    ]

    expi = 'topic'
    root = os.path.abspath('../..')
    # result = pickle.load(open('result.pkl', 'rb')) if os.path.isfile('result.pkl') else []
    result = []
    
    for dataset in datasets:
        for model in models:
            for predict_mode in predict_modes:
                if predict_mode == 'top':
                    data = {'dataset': [], 'model': [], 'cc': [], 'lw': [], 'n': [], 'score': [], 'predict_mode': [], 'tl': []}
                    subprocess.call(['python', 'predict_one.py', dataset, model, predict_mode, '>log.txt', '2>&1'])
                else:
                    data = {'dataset': [], 'model': [], 'cc': [], 'lw': [], 'n': [], 'score': [], 'predict_mode': []}
                    subprocess.call(['python', 'predict_one.py', dataset, model, predict_mode, '>log.txt', '2>&1'])
                result += pickle.load(open('result_one.pkl', 'rb'))
                pickle.dump(result, open('result.pkl', 'wb'))
    # print (result)
    
    for i in result:
        for k in data.keys():
            data[k].append(i[k])
    df = pd.DataFrame(data=data)
    if 'top' in predict_modes:
        df = df.groupby(['dataset', 'cc', 'model', 'predict_mode', 'tl']).min().reset_index()
    else:
        df = df.groupby(['dataset', 'cc', 'model', 'predict_mode']).min().reset_index()
    df.to_csv('{root:s}/Score/{expi:s}/timepred_{date:s}.csv'.format(root=root, expi=expi, date=str(datetime.datetime.now())).replace(":", "-"), index=False)