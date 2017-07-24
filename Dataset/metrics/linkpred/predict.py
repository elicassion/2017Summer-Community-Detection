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
        'bigclam',
        'cdot',
    ]
    modes = [
      'cite', 
      # 'coau'
    ]
    conferences = [
      # 'AAAI', 
      # 'ACL', 
      'SIGCOMM'
    ]
    versions = {
        'cdot': [
            # ('CDOT2', 100),
            # ('CDOT3', 100),
            # ('CDOT8', 100),
            # ('CDOT_L0', 19),
            # ('CDOT_L0_071923', 19),
            # ('CDOT_L0_ori', 19),
            # ('CDOT_L0_072317', 19),
            # ('CDOT_L0_072417', 19), # ACL
            # ('CDOT_L1_072416', 287),
            ('CDOT_L0_072418', 19), # SIGCOMM

        ],
        'bigclam': [
            # ('bigclam_100', 100),
            # ('bigclam_L0_072416', 19), # ACL
            # ('bigclam_L1_072416', 287),
            ('bigclam_L0_072417', 19), # SIGCOMM
        ]
    }
    dataset_path = 'data'
    expi = 'link_pred'
    root = os.path.abspath(os.path.join('..', '..'))
    result = pickle.load(open('result.pkl', 'rb')) if os.path.isfile('result.pkl') else []
    data = {'model': [], 'cc': [], 'n': [], 'score': [], 'mode': [], 'conference': [], 'version':[]}
    for model in models:
        for mode in modes:
            for conference in conferences:
                if versions[model]:
                    for version in versions[model]:
                        subprocess.run('python predict_batch.py {0:s} {1:s} {2:s} {3:s} {4:s} {5:d}'.format(dataset_path, model, mode, conference, version[0], version[1]), shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
                        result += pickle.load(open('result_batch.pkl', 'rb'))
                else:
                    subprocess.run('python predict_batch.py {0:s} {1:s} {2:s} {3:s} {4:s} {5:d}'.format(dataset_path, model, mode, conference, '', 100), shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
                    result += pickle.load(open('result_batch.pkl', 'rb'))
                pickle.dump(result, open('result.pkl', 'wb'))   
    for i in result:
        for k in data.keys():
            data[k].append(i[k])
    df = pd.DataFrame(data=data)
    df = df.ix[df.groupby(['model', 'mode', 'conference', 'version'])['score'].idxmax().values, :].reset_index(drop=True)
    out_filename = os.path.join(root, 'measure', expi, 'link_pred_{date:s}.csv'.format(date=str(datetime.datetime.now()).replace(":", "-")))
    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename))
    df.to_csv(out_filename, index=False)
    os.remove('result_batch.pkl')
    os.remove('result.pkl')
