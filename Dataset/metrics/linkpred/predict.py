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
    datasets = [
       'MAG/01_MAG_Internet_privacy',
       'MAG/02_MAG_Theoretical_computer_science',
       'MAG/03_MAG_Computer_graphics_images',
       'MAG/04_MAG_Computer_hardware',
       'MAG/05_MAG_Computational_biology',
       'MAG/06_MAG_Computational_science',
       'MAG/07_MAG_Knowledge_management',
       'MAG/08_MAG_Operations_research',
       'MAG/09_MAG_Information_retrieval',
       'MAG/10_MAG_Natural_language_processing',
       'MAG/11_MAG_Computer_architecture',
       'MAG/12_MAG_Real-time_computing',
       'MAG/13_MAG_Distributed_computing',
       'MAG/14_MAG_Speech_recognition',
       'MAG/15_MAG_Cognitive_science',
       'MAG/16_MAG_Mental_health',
       'MAG/17_MAG_Computer_security',
       'MAG/18_MAG_Pattern_recognition',
       'MAG/19_MAG_Data_mining',
       'MAG/20_MAG_Database',
       'MAG/21_MAG_World_Wide_Web',
       'MAG/22_MAG_Computer_network',
       'MAG/23_MAG_Parallel_computing',
       'MAG/24_MAG_Embedded_system',
       'MAG/25_MAG_Algorithm',
       'MAG/26_MAG_Operating_system',
       'MAG/27_MAG_Programming_language',
       'MAG/28_MAG_Telecommunications',
       'MAG/29_MAG_Artificial_intelligence',
       'MAG/30_MAG_Computer_vision',
       'MAG/31_MAG_Machine_learning',
      'MAG/32_MAG_new_Bioinformatics',
    ]

    expi = 'link_pred'
    root = os.path.abspath('../..')
    result = pickle.load(open('result.pkl', 'rb')) if os.path.isfile('result.pkl') else []
    data = {'dataset': [], 'model': [], 'cc': [], 'n': [], 'score': []}
    for dataset in datasets:
        for model in models:
            subprocess.run('python predict_batch.py {0:s} {1:s}'.format(dataset, model), shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
            result += pickle.load(open('result_batch.pkl', 'rb'))
            pickle.dump(result, open('result.pkl', 'wb'))
    for i in result:
        for k in data.keys():
            data[k].append(i[k])
    df = pd.DataFrame(data=data)
    df = df.ix[df.groupby(['dataset', 'cc', 'model'])['score'].idxmax().values, :].reset_index(drop=True)
    out_filename = '{root:s}/Scores/{expi:s}/link_pred_{date:s}.csv'.format(root=root, expi=expi, date=str(datetime.datetime.now()).replace(":", "-"))
    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename))
    df.to_csv(out_filename, index=False)
