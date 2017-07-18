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
        # 'MAGIC',
        # 'BIGCLAM',
        'CODA',
    ]
    modes = [
      'cite', 
      # 'coau'
    ]
    conference = [
      'AAAI', 
      # 'ACL', 
      # 'SIGCOMM'
    ]
    dataset_path = 'data'
    expi = 'link_pred'
    root = os.path.abspath(os.path.join('..', '..'))
    result = pickle.load(open('result.pkl', 'rb')) if os.path.isfile('result.pkl') else []
    data = {'model': [], 'cc': [], 'n': [], 'score': [], 'mode': [], 'conference': []}
    for model in models:
        for mode in modes:
            subprocess.run('python predict_batch.py {0:s} {1:s} {2:s} {3:s}'.format(dataset_path, model, mode, conference), shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
            result += pickle.load(open('result_batch.pkl', 'rb'))
            pickle.dump(result, open('result.pkl', 'wb'))
    for i in result:
        for k in data.keys():
            data[k].append(i[k])
    df = pd.DataFrame(data=data)
    df = df.ix[df.groupby(['dataset', 'cc', 'model'])['score'].idxmax().values, :].reset_index(drop=True)
    out_filename = os.path.join(root, 'measure', expi, 'link_pred_{date:s}.csv'.format(date=str(datetime.datetime.now()).replace(":", "-")))
    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename))
    df.to_csv(out_filename, index=False)
