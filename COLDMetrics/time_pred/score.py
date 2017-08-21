import os
import copy
import sys
import random
import gc
import datetime
import numpy as np
import pandas as pd


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def calc_score(args):
    print(datetime.datetime.now(), args)
    sys.stdout.flush()
    model2score_prefix = {
        'CTCDPoi': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'CTCDBer': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLDSlice': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLD': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
    }
    args['score_prefix'] = model2score_prefix[args['model']].format(**args)
    if not os.path.exists(args['score_prefix'] + '.txt'):
        return 0
    times = np.loadtxt(args['score_prefix'] + '.txt')
    score = np.mean(np.abs(times[:, 0] - times[:, 1]))
    print('score', score)
    return score


if __name__ == '__main__':
    models = [
        # 'CTCDPoi',
        # 'CTCDBer',
        # 'COLDSlice',
        'COLD',
    ]
    datasets = [
        'AAAI',
        'SIGCOMM',
        # 'dblp_citation',
        # 'dblp_coauthor',
        # 'weibo',
    ]
    community_count = [
        19,
        287,
        265,
        # 10,
        # 50,
        # 100,
        # 150,
    ]

    exp = 'time_pred'
    root = os.path.abspath('../..')
    data = {'dataset': [], 'model': [], 'cc': [], 'lw': [], 'n': [], 'score': []}
    for dataset in datasets:
        for model in models:
            for cc in community_count:
                for lw in [16, 32, 48, 64] if 'CTCD' in model else [32]:
                    if 'CTCD' in model:
                        for n in range(0, 300, 10):
                            score = calc_score({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': '%04d' % n})
                            data['dataset'].append(dataset)
                            data['model'].append(model)
                            data['cc'].append(cc)
                            data['lw'].append(lw)
                            data['n'].append(n)
                            data['score'].append(score)
                            gc.collect()
                    score = calc_score({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final'})
                    data['dataset'].append(dataset)
                    data['model'].append(model)
                    data['cc'].append(cc)
                    data['lw'].append(lw)
                    data['n'].append(300)
                    data['score'].append(score)
                    gc.collect()
    df = pd.DataFrame(data=data)
    df.to_csv('{root:s}/Score/{exp:s}/time_pred_score_{time:s}.csv'.format(root=root, exp=exp, time=str(datetime.datetime.now())), index=False)
    print('all done')
