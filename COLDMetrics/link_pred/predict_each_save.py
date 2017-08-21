import os
import copy
import sys
import random
import gc
import datetime
sys.path.append(os.path.abspath('..'))
from COLD.predictor import predictor as COLDPredictor
from CTCD.ber_predictor import predictor as CTCDBerPredictor
from CTCD.poi_predictor import predictor as CTCDPoiPredictor
from BIGCLAM.predictor import predictor as BIGCLAMPredictor


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def load_edges(data_dir, predictor):
    edges = []
    user_pair = set()
    for line in open(os.path.join(data_dir, 'links.txt')):
        line = line.strip().split('\t')
        if line[0] not in predictor.uname2uid:
            continue
        if line[1] not in predictor.uname2uid:
            continue
        uid0 = predictor.uname2uid[line[0]]
        uid1 = predictor.uname2uid[line[1]]
        user_pair.add((uid0, uid1))
        for time_pair in line[2:]:
            time_pair = time_pair.split()
            edges.append((uid0, uid1, int(time_pair[0]), int(time_pair[1])))
    max_time = max(i for edge in edges for i in edge[-2:]) + 1
    min_time = min(i for edge in edges for i in edge[-2:]) - 1
    for i in range(len(edges)):
        edge = edges[i]
        edges[i] = (edge[0], edge[1], (edge[2] - min_time) / (max_time - min_time), (edge[3] - min_time) / (max_time - min_time))
    return user_pair, edges


def prdict_pos(predictor, edges, num):
    scores = []
    count = 0
    for edge in random.sample(edges, num):
        if count % 100000 == 0:
            print(datetime.datetime.now(), 'pos: ', count)
            sys.stdout.flush()
        count += 1
        scores.append(predictor.link_predict(*edge))
    return scores


def prdict_neg(predictor, user_pair, num):
    scores = []
    for i in range(num):
        if i % 100000 == 0:
            print(datetime.datetime.now(), 'neg: ', i)
            sys.stdout.flush()
        while True:
            from_user = random.randint(0, len(predictor.uname2uid) - 1)
            to_user = random.randint(0, len(predictor.uname2uid) - 1)
            if (from_user, to_user) not in user_pair:
                break
        time1 = random.random()
        time2 = random.random()
        scores.append(predictor.link_predict(from_user, to_user, time1, time2))
    return scores


def load_data(args):
    model2predictor = {
        'CTCDPoi': ctcd_poi_predictor,
        'CTCDBer': ctcd_ber_predictor,
        'COLD': cold_predictor,
        'BIGCLAM': bigclam_predictor,
    }
    predictor = model2predictor[args['model']]
    data_dir = '{root:s}/Data/{exp:s}/{dataset:s}/'.format(**args)
    predictor.load_data(data_dir)


def prdict(args):
    print(datetime.datetime.now(), args)
    sys.stdout.flush()
    model2predictor = {
        'CTCDPoi': ctcd_poi_predictor,
        'CTCDBer': ctcd_ber_predictor,
        'COLD': cold_predictor,
        'BIGCLAM': bigclam_predictor,
    }
    model2score_prefix = {
        'CTCDPoi': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{it:s}',
        'CTCDBer': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{it:s}',
        'COLD': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{it:s}',
        'BIGCLAM': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}',
    }
    args['score_prefix'] = model2score_prefix[args['model']].format(**args)
    mkdir_if_not_exists(os.path.split(args['score_prefix'])[0])
    model2result_prefix = {
        'CTCDPoi': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{it:s}',
        'CTCDBer': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{it:s}',
        'COLD': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{it:s}',
        'BIGCLAM': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}',
    }
    args['data_dir'] = '{root:s}/Data/{exp:s}/{dataset:s}/'.format(**args)
    args['result_prefix'] = model2result_prefix[args['model']].format(**args)
    if os.path.isfile(args['score_prefix'] + '.txt'):
        return
    predictor = model2predictor[args['model']]

    predictor.load_result(args['result_prefix'])
    print(datetime.datetime.now(), 'predictor init done')
    sys.stdout.flush()

    user_pair, edges = load_edges(args['data_dir'], predictor)
    print(datetime.datetime.now(), 'load edges done')
    sys.stdout.flush()

    score_pos = prdict_pos(predictor, edges, int(len(edges) * 0.1))
    print(datetime.datetime.now(), 'predict pos done')
    sys.stdout.flush()

    score_neg = prdict_neg(predictor, user_pair, int(len(edges) * 0.1))
    print(datetime.datetime.now(), 'predict neg done')
    sys.stdout.flush()

    fp = open(args['score_prefix'] + '.txt', 'w')
    for score in score_pos:
        fp.write('%f\t1\n' % score)
    print(datetime.datetime.now(), 'save pos done')
    sys.stdout.flush()

    for score in score_neg:
        fp.write('%f\t0\n' % score)
    print(datetime.datetime.now(), 'save neg done')
    sys.stdout.flush()

    fp.close()


if __name__ == '__main__':
    models = [
        'CTCDPoi',
        'CTCDBer',
    ]
    datasets = [
        'dblp_citation',
        # 'dblp_coauthor',
        # 'weibo',
    ]
    community_count = [
        10,
        50,
        # 100,
        # 150,
    ]
    ctcd_poi_predictor = COLDPredictor()
    ctcd_ber_predictor = CTCDBerPredictor()
    cold_predictor = CTCDPoiPredictor()
    bigclam_predictor = BIGCLAMPredictor()

    exp = 'topic'
    root = os.path.abspath('../..')
    for dataset in datasets:
        for model in models:
            load_data({'exp': exp, 'root': root, 'model': model, 'dataset': dataset})
            for cc in community_count:
                for lw in [16, 32, 48, 64] if 'CTCD' in model else [32]:
                    for it in range(0, 310, 10):
                        prdict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'it': ('%04d' % it) if it < 300 else 'final'})
                        gc.collect()
