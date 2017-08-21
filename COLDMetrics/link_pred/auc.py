import os
import pandas as pd
import copy
import sys
import subprocess
import random
from sklearn.metrics import roc_auc_score
import datetime


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def calc_auc(args):
    print(datetime.datetime.now(), args)
    sys.stdout.flush()
    model2score_prefix = {
        'CTCDPoi': '{root:s}/Score/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'CTCDBer': '{root:s}/Score/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLDSlice': '{root:s}/Score/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLD': '{root:s}/Score/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'BIGCLAM': '{root:s}/Score/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}',
         'PMTLM':'{root:s}/Score/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}',
    }
    args['score_prefix'] = model2score_prefix[args['model']].format(**args)
    scores = []
    labels = []
    if not os.path.exists(args['score_prefix'] + '.txt'):
        return 0
    for line in open(args['score_prefix'] + '.txt'):
        line = line.split()
        scores.append(float(line[0]))
        labels.append(int(line[1]))
    print(datetime.datetime.now(), 'load done')
    sys.stdout.flush()
    auc = roc_auc_score(labels, scores)
    print(datetime.datetime.now(), 'calc auc done', auc)
    sys.stdout.flush()
    return auc


if __name__ == '__main__':
    models = [
        #'CTCDPoi',
        #'CTCDBer',
        #'COLDSlice',
        #'COLD',
        #'BIGCLAM',
	'PMTLM',
    ]
    datasets = [
        'dblp_citation',
         'dblp_coauthor',
         'weibo',
    ]
    community_count = [
         10,
         50,
        100,
         150,
    ]
    exp = 'link_pred'
    root = os.path.abspath('../..')
    data = {'dataset': [], 'model': [], 'cc': [], 'lw': [], 'n': [], 'auc': []}
    for dataset in datasets:
        for model in models:
            for cc in community_count:
                for lw in [16, 32, 48, 64] if 'CTCD' in model else [32]:
                    if 'CTCD' in model and False:
                        for n in range(0, 300, 10):
                            auc = calc_auc({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': '%04d' % n})
                            data['dataset'].append(dataset)
                            data['model'].append(model)
                            data['cc'].append(cc)
                            data['lw'].append(lw)
                            data['n'].append(n)
                            data['auc'].append(auc)
                    auc = calc_auc({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final'})
                    data['dataset'].append(dataset)
                    data['model'].append(model)
                    data['cc'].append(cc)
                    data['lw'].append(lw)
                    data['n'].append(300)
                    data['auc'].append(auc)
    df = pd.DataFrame(data=data)
    df.to_csv('{root:s}/Score/{exp:s}/auc_{time:s}.csv'.format(root=root, exp=exp, time=str(datetime.datetime.now())), index=False)
    print('all done')
