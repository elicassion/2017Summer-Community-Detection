import os
import copy
import sys
import random
import gc
import datetime
import subprocess
import pickle
import pandas as pd
import numpy as np


if __name__ == '__main__':
    # Parameters
    models = [
        # 'MAGIC',
        # 'bigclam',
        'cdot',
    ]
    modes = [
      'cite', 
      # 'coau'
    ]
    conferences = [
      'AAAI', 
      # 'ACL', 
      # 'SIGCOMM'
    ]
    versions = {
        'cdot': [
            # ('CDOT2', 100),
            # ('CDOT3', 100),
            # ('CDOT8', 100),
            # ('CDOT_L0', 19),
            # ('CDOT_L0_071923', 19),
            # ('CDOT_L0_ori', 19),
            ('CDOT_L0_072317', 19),
        ],
        'bigclam': [
            ('bigclam_100', 100),
        ]
    }
    tolerations = np.linspace(0.1, 1, 10).tolist()
    predict_modes = [
        'topk',
        # 'map'
    ]
    # Call predictions for each set of parameters
    dataset_path = 'data'
    expi = 'time_pred'
    root = os.path.abspath(os.path.join('..', '..'))
    result = pickle.load(open('result.pkl', 'rb')) if os.path.isfile('result.pkl') else []
    data = {'model': [], 'cc': [], 'n': [], 'score': [], 'mode': [], 'conference': [], 'version':[], 'toleration':[]}
    for model in models:
        for mode in modes:
            for conference in conferences:
                if versions[model]:
                    for version in versions[model]:
                        for toleration in tolerations:
                            for predict_mode in predict_modes:
                                subprocess.run('python predict_batch.py {0:s} {1:s} {2:s} {3:s} {4:s} {5:d} {6:.1f} {7:s}'.format(dataset_path, model, mode, conference, version[0], version[1], toleration, predict_mode), shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
                                result += pickle.load(open('result_batch.pkl', 'rb'))
                else:
                    for toleration in tolerations:
                        for predict_mode in predict_modes:
                            subprocess.run('python predict_batch.py {0:s} {1:s} {2:s} {3:s} {4:s} {5:d} {6:.1f} {7:s}'.format(dataset_path, model, mode, conference, '', 100, toleration, predict_mode), shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
                            result += pickle.load(open('result_batch.pkl', 'rb'))
                pickle.dump(result, open('result.pkl', 'wb'))   
    for i in result:
        for k in data.keys():
            data[k].append(i[k])
    df = pd.DataFrame(data=data)
    df = df.ix[df.groupby(['model', 'mode', 'conference', 'version', 'toleration'])['score'].idxmax().values, :].reset_index(drop=True)
    out_filename = os.path.join(root, 'measure', expi, '{expi:s}_{date:s}.csv'.format(expi=expi, date=str(datetime.datetime.now()).replace(":", "-")))
    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename))
    df.to_csv(out_filename, index=False)
    os.remove('result_batch.pkl')
    os.remove('result.pkl')
