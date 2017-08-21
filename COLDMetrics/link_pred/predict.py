import os
import copy
import sys
import random
import gc
import datetime
sys.path.append(os.path.abspath('..'))
from COLD.slice_predictor import predictor as COLDSlicePredictor
from COLD.predictor import predictor as COLDPredictor
from CTCD.ber_predictor import predictor as CTCDBerPredictor
from CTCD.poi_predictor import predictor as CTCDPoiPredictor
from BIGCLAM.predictor import predictor as BIGCLAMPredictor
from PMTLM.predictor import predictor as PMTLMPredictor
from sklearn.metrics import roc_auc_score

def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def load_edges(data_dir, predictor):
    edges = []
    user_pair = set()
    print ("edges dir is ",data_dir)
    cnt = 0
    for line in open(os.path.join(data_dir, 'del_links.txt')):
        line = line.strip().split('\t')
        cnt = cnt +1
        if line[0] not in predictor.uname2uid:
            print (line[0]+" is not in dict")
            continue
        if line[1] not in predictor.uname2uid:
            print (line[1]+" is not in dict")
            continue
        uid0 = predictor.uname2uid[line[0]]
        uid1 = predictor.uname2uid[line[1]]
        user_pair.add((uid0, uid1))
        for time_pair in line[2:]:
            time_pair = time_pair.split()
            edges.append((uid0, uid1, int(time_pair[0]), int(time_pair[1])))
    print("the user_pair is ",cnt)
    max_time = max(i for edge in edges for i in edge[-2:]) + 1
    min_time = min(i for edge in edges for i in edge[-2:]) - 1
    for i in range(len(edges)):
        edge = edges[i]
        edges[i] = (edge[0], edge[1], (edge[2] - min_time) / (max_time - min_time), (edge[3] - min_time) / (max_time - min_time))
    print (str(len(edges))+" = len(edges)")
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
        'COLDSlice': cold_slice_predictor,
        'COLD': cold_predictor,
        'BIGCLAM': bigclam_predictor,
         'PMTLM':pmtlm_predictor

    }
    predictor = model2predictor[args['model']]
    data_dir = '{root:s}/Data/{exp:s}/{dataset:s}/'.format(**args)
    predictor.load_data(data_dir)
    global user_pair, edges
    user_pair, edges = load_edges(data_dir, predictor)
    print(datetime.datetime.now(), 'load edges done')
    sys.stdout.flush()


def prdict(args):
    print(datetime.datetime.now(), args)
    sys.stdout.flush()
    model2predictor = {
        'CTCDPoi': ctcd_poi_predictor,
        'CTCDBer': ctcd_ber_predictor,
        'COLDSlice': cold_slice_predictor,
        'COLD': cold_predictor,
        'BIGCLAM': bigclam_predictor,
        'PMTLM':pmtlm_predictor
    }
    model2result_prefix = {
        'CTCDPoi': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'CTCDBer': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLDSlice': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLD': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'BIGCLAM': '{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}',
        'PMTLM':'{root:s}/Result/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}',
    }
    args['data_dir'] = '{root:s}/Data/{exp:s}/{dataset:s}/'.format(**args)
    args['result_prefix'] = model2result_prefix[args['model']].format(**args)
    model2score_prefix = {
        'CTCDPoi': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/linkpred/cc{cc:d}_lw{lw:d}_{n:s}',
        'CTCDBer': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/linkpred/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLDSlice': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/linkpred/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLD': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/linkpred/cc{cc:d}_lw{lw:d}_{n:s}',
        'BIGCLAM': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/linkpred/cc{cc:d}_lw{lw:d}',
        'PMTLM':'{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/linkpred/cc{cc:d}_lw{lw:d}',
    }
    args['score_prefix'] = model2score_prefix[args['model']].format(**args)
    # if os.path.exists(args['score_prefix'] + '.txt'):
    #     print (args['score_prefix'] + '.txt')
    #     print ("already exist")
    #     return
    mkdir_if_not_exists(os.path.split(args['score_prefix'])[0])
    predictor = model2predictor[args['model']]
    print ("now load result")
    predictor.load_result(args['result_prefix'])
    print(datetime.datetime.now(), 'predictor init done')
    sys.stdout.flush()

    score_pos = prdict_pos(predictor, edges, int(len(edges) * 0.1))
    print(datetime.datetime.now(), 'predict pos done')
    sys.stdout.flush()

    score_neg = prdict_neg(predictor, user_pair, int(len(edges) * 0.1))
    print(datetime.datetime.now(), 'predict neg done')
    sys.stdout.flush()

    pos_fp = open(args['score_prefix'] + '.pos.txt', 'w')
    for score in score_pos:
        pos_fp.write('%f\n' % score)
    print(datetime.datetime.now(), 'save pos done')
    sys.stdout.flush()

    neg_fp = open(args['score_prefix'] + '.neg.txt', 'w')
    for score in score_neg:
        neg_fp.write('%f\n' % score)
    print(datetime.datetime.now(), 'save neg done')
    sys.stdout.flush()

    pos_fp.close()
    neg_fp.close()


    # pos_score = [float(line) for line in open(os.path.join(args['score_prefix'], args['n'] + '.pos.txt'))]
    # neg_score = [float(line) for line in open(os.path.join(args['score_prefix'], args['n'] + '.neg.txt'))]
    auc = roc_auc_score([1] * len(score_pos) + [0] * len(score_neg), score_pos + score_neg)
    print(datetime.datetime.now(), 'auc: ', auc)

    auc_fp = open(args['score_prefix'] + '.auc.txt', 'w')
    auc_fp.write(str(auc))
    auc_fp.close()


if __name__ == '__main__':
    models = [
        #'CTCDPoi',
        #'CTCDBer',
        # 'COLDSlice',
        'COLD',
        #'BIGCLAM',
        # 'PMTLM',
    ]
    datasets = [
        'AAAI',
        # 'SIGCOMM'
        # 'dblp_citation',
        # 'dblp_coauthor',
        # 'weibo',
    ]
    community_count = [
        19,
        # 265,
        287,
        # 10,
        # 50,
        # 100,
        # 150,
    ]
    ctcd_poi_predictor = CTCDPoiPredictor()
    ctcd_ber_predictor = CTCDBerPredictor()
    cold_slice_predictor = COLDSlicePredictor()
    cold_predictor = COLDPredictor()
    bigclam_predictor = BIGCLAMPredictor()
    pmtlm_predictor = PMTLMPredictor()
    exp = 'topic'
    root = os.path.abspath('../..')
    for dataset in datasets:
        for model in models:
            load_data({'exp': exp, 'root': root, 'model': model, 'dataset': dataset})
            for cc in community_count:
                for lw in [16, 32, 48, 64] if 'CTCD' in model else [32]:
                    prdict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final'})
                    gc.collect()
