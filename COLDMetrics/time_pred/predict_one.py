import os
import copy
import sys
import random
import gc
import datetime
import ujson
from multiprocessing.pool import Pool
import pickle
sys.path.append(os.path.abspath('..'))
from COLD.slice_predictor import predictor as COLDSlicePredictor
from COLD.predictor import predictor as COLDPredictor
from CTCD.ber_predictor import predictor as CTCDBerPredictor
from CTCD.poi_predictor import predictor as CTCDPoiPredictor
import numpy as np


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        while True:
            try:
                os.makedirs(path)
                break
            except:
                if os.path.exists(path):
                    break


def load_docs(data_dir, predictor):
    docs = []
    for line in open(os.path.join(data_dir, 'docs.txt')):
        line = line.strip().split('\t', maxsplit=2)
        if line[0] not in predictor.uname2uid:
            continue
        uid = predictor.uname2uid[line[0]]
        if len(line) > 2:
            docs.append((' '.join('%x' % predictor.word2wid[i] for i in line[2].split() if i in predictor.word2wid), uid, predictor.norm_time(int(line[1]))))
    return docs


def predict_time(predictor, pred_mode, docs, num):
    count = 0
    real_times = []
    pred_times = []
    likelihoods = []
    # for doc in random.sample(docs, num):
    for doc in docs:
        if count % 100000 == 0:
            print(datetime.datetime.now(), 'doc: ', count)
            sys.stdout.flush()
        count += 1
        # a doc: text, uid, time
        if pred_mode == 'top':
            time = predictor.time_predict(pred_mode, doc)
            real_times.append(doc[2])
            pred_times.append(time)
            return real_times, pred_times
        elif predict_mode == 'nlog':
            likelihood = predictor.time_predict(pred_mode, doc)
            likelihoods.append(likelihood)
    if pred_mode == 'top':
        return real_times, pred_times
    elif pred_mode == 'nlog':
        return likelihoods


def load_data(args):
    model2predictor = {
        'CTCDPoi': ctcd_poi_predictor,
        'CTCDBer': ctcd_ber_predictor,
        'COLDSlice': cold_slice_predictor,
        'COLD': cold_predictor,
    }
    predictor = model2predictor[args['model']]
    data_dir = '{root:s}/Data/topic/{dataset:s}/'.format(**args)
    predictor.load_data(data_dir)
    docs = load_docs(data_dir, predictor)
    random.seed(1)
    docs = random.sample(docs, int(len(docs) * 0.1))
    del predictor
    print(datetime.datetime.now(), 'load data done')
    sys.stdout.flush()
    return docs


def predict(args):
    print(datetime.datetime.now(), args)
    sys.stdout.flush()
    model2predictor = {
        'CTCDPoi': ctcd_poi_predictor,
        'CTCDBer': ctcd_ber_predictor,
        'COLDSlice': cold_slice_predictor,
        'COLD': cold_predictor,
    }
    model2result_prefix = {
        'CTCDPoi': '{root:s}/Result/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'CTCDBer': '{root:s}/Result/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLDSlice': '{root:s}/Result/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLD': '{root:s}/Result/topic/{dataset:s}/{model:s}/cc{cc:d}_lw{lw:d}_{n:s}',
    }
    args['data_dir'] = '{root:s}/Data/{exp:s}/{dataset:s}/'.format(**args)
    args['result_prefix'] = model2result_prefix[args['model']].format(**args)
    model2score_prefix = {
        'CTCDPoi': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/timepred/cc{cc:d}_lw{lw:d}_{n:s}',
        'CTCDBer': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/timepred/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLDSlice': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/timepred/cc{cc:d}_lw{lw:d}_{n:s}',
        'COLD': '{root:s}/Score/{exp:s}/{dataset:s}/{model:s}/timepred/cc{cc:d}_lw{lw:d}_{n:s}',
    }
    args['score_prefix'] = model2score_prefix[args['model']].format(**args)
    mkdir_if_not_exists(os.path.split(args['score_prefix'])[0])
    
    docs = ujson.load(open('docs.json'))
    predictor = model2predictor[args['model']]

    predictor.load_result(args['result_prefix'])
    print (datetime.datetime.now(), 'Predictor Init Done.')
    sys.stdout.flush()
    if predict_mode == 'top':
        if os.path.isfile(args['score_prefix'] + '.top.txt'):
            # real_times, pred_times = zip([float(i) for i in line.split()] for line in open(args['score_prefix'] + '.txt'))
            # real_times, pred_times = zip([float(i) for i in line.split()] for line in open(args['score_prefix'] + '.txt'))
            score_res = np.loadtxt(args['score_prefix'] + '.top.txt')
            real_times = score_res[:,0].tolist()
            pred_times = score_res[:,1].tolist()
        else:
            real_times, pred_times = predict_time(predictor, args['predict_mode'], docs, int(len(docs) * 0.2))
            print (datetime.datetime.now(), 'Predict Time Done.')
            sys.stdout.flush()

            fp = open(args['score_prefix'] + '.top.txt', 'w')
            for rt, pt in zip(real_times, pred_times):
                fp.write('%f\t%f\n' % (rt, pt))
            fp.close()
            print (datetime.datetime.now(), 'Save Time Done.')
            sys.stdout.flush()
        score = sum(1 for pair in zip(real_times, pred_times) if abs(pair[0] - pair[1]) < args['tl']) / len(real_times)
    elif predict_mode == 'nlog':
        if os.path.isfile(args['score_prefix'] + '.nlog.txt'):
            likelihoods = np.loadtxt(args['score_prefix'] + '.nlog.txt')
        else:
            likelihoods = predict_time(predictor, args['predict_mode'], docs, int(len(docs) * 0.2))
            print (datetime.datetime.now(), 'Predict Time Done.')
            sys.stdout.flush()
            fp = open(args['score_prefix'] + '.nlog.txt', 'w')
            for rt, pt in likelihoods:
                fp.write('%f\t%f\n' % (rt, pt))
            fp.close()
            print (datetime.datetime.now(), 'Save Time Done.')
            sys.stdout.flush()
        score = sum(likelihoods) / len(likelihoods)
    print(datetime.datetime.now(), 'Calc Score Done.')
    sys.stdout.flush()
    args['score'] = score
    return args


if __name__ == '__main__':
    dataset = sys.argv[1]
    model = sys.argv[2]
    predict_mode = sys.argv[3]
    community_count = [
        19,
        287,
        # 265,
        # 10,
        # 50,
        # 100,
        # 150,
    ]
    tolerence = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    ctcd_poi_predictor = CTCDPoiPredictor()
    ctcd_ber_predictor = CTCDBerPredictor()
    cold_slice_predictor = COLDSlicePredictor()
    cold_predictor = COLDPredictor()

    exp = 'topic'
    root = os.path.abspath('../..')
    docs = load_data({'exp': exp, 'root': root, 'model': model, 'dataset': dataset})
    ujson.dump(docs, open('docs.json', 'w'))
    del docs
    result = []
    to_pred = []
    for cc in community_count:
        for lw in [16, 32, 48, 64] if 'CTCD' in model else [32]:
            if predict_mode == 'top':
                for tl in tolerence:
                    to_pred.append({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final', 'predict_mode': predict_mode, 'tl': tl})
            elif predict_mode == 'nlog':
                to_pred.append({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final', 'predict_mode': predict_mode})
            # predict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final'})
            gc.collect()
            # if 'CTCD' in model:
            #     for n in range(0, 300, 10):
            #         to_pred.append({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': '%04d' % n})
            #         predict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': '%04d' % n})
    result += Pool(20).map(predict, [i for i in to_pred], chunksize=1)
    pickle.dump(result, open('result_one.pkl', 'wb'))
