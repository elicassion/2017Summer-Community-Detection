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
      # 'cite', 
      # 'coau',
      's_cite',
    ]
    conferences = [
      'AAAI', # 19 287 1287 
      # 'ACL', # 19 278 1204 
      # 'SIGCOMM' # 19 265 1060 
    ]
    versions = {
        'cdot': {
            'AAAI':[ 
                # ('CDOT2', 100),
                # ('CDOT3', 100),
                # ('CDOT8', 100),
                # ('CDOT_L0', 19),
                # ('CDOT_L0_071923', 19),
                # ('CDOT_L0_ori', 19),
                # ('CDOT_L0_072317', 19),
                # ('CDOT_L1_072416', 287),
                # ('CDOT_L2_072422', 1287),
                # ('CDOT_L0_072518', 19),
                # ('CDOT_L1_072518', 287),
                # ('CDOT_L0_072522', 19),
                # ('CDOT_L1_072522', 287),
                # ('CDOT_L0_072910', 19),
                # ('CDOT_L1_073110', 287),
                # ('CDOT_L1_073112', 287),
                # ('CDOT_L1_073116', 287),
                # ('CDOT_L1_073120', 287),
                ('CDOT_L1_080101', 287),
            ],
            'ACL':[ 
                # ('CDOT_L0_072417', 19), # ACL
                # ('CDOT_L1_072422', 278), # ACL
                ('CDOT_L0_072521', 19), # ACL
                ('CDOT_L1_072521', 278), # ACL
            ],
            'SIGCOMM':[
                # ('CDOT_L0_072418', 19), # SIGCOMM
                # ('CDOT_L1_072422', 265), #SIGCOMM
                # ('CDOT_L0_072518', 19), # SIGCOMM
                # ('CDOT_L0_072521', 19), # SIGCOMM
                # ('CDOT_L1_072518', 265), #SIGCOMM
                # ('CDOT_L1_072522', 265), #SIGCOMM
                ('CDOT_L0_072816', 19), #SIGCOMM
            ]
        },
        'bigclam': {
            'AAAI':[
                # ('bigclam_100', 100),
                # ('bigclam_L1_072416', 287),
                # ('bigclam_L2_072414', 1287),
                # ('bigclam_L0_072518', 19),
                # ('bigclam_L1_072518', 287),
            ],
            'ACL':[
                # ('bigclam_L0_072416', 19), # ACL
                # ('bigclam_L1_072416', 278), # ACL
                # ('bigclam_L2_072500', 1204), # ACL
                ('bigclam_L0_072521', 19), # ACL
                ('bigclam_L1_072521', 278), # ACL
            ],
            'SIGCOMM':[
                # ('bigclam_L0_072417', 19), # SIGCOMM
                # ('bigclam_L1_072417', 265), # SIGCOMM
                # ('bigclam_L2_072500', 1060), # SIGCOMM
                # ('bigclam_L0_072518', 19), # SIGCOMM
                # ('bigclam_L0_072521', 19), # SIGCOMM
                # ('bigclam_L1_072518', 265), # SIGCOMM
            ]

        }
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
                    for version in versions[model][conference]:
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
