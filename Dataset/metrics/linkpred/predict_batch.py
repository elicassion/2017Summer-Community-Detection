import os
import copy
import sys
import random
import subprocess
import gc
import datetime
import ujson
from multiprocessing.pool import Pool
from multiprocessing import current_process
import pickle
from sklearn.metrics import roc_auc_score
# sys.path.append(os.path.abspath('..'))
from bigclam.predictor import predictor as BIGCLAMPredictor
from cdot.predictor import predictor as CDOTPredictor


def genearate_tmp_filename(s):
    return ('tmp-' + str(hash(s)) + str(datetime.datetime.now()) + '.txt').replace(' ', '_').replace(':', '_')


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        while True:
            try:
                os.makedirs(path)
                break
            except:
                if os.path.exists(path):
                    break

# load edges dict version
# def load_edges(data_dir, predictor):
#     edges = dict()
#     for line in open(os.path.join(data_dir, 'link.txt')):
#         # line = [i for i in line.split() if i in predictor.uname2uid]
#         # print(line)
#         line = [i for i in line.split('\t')]
#         doc_id = predictor.uname2uid[line[0]]
#         ref_id = predictor.uname2uid[line[1]]
#         if (ref_id, doc_id) not in edges.keys():
#             edges[(ref_id, doc_id)] = set()
#         for tpl in line[2:-1]:
#             tp = tpl.split(' ')
#             edges[(ref_id, doc_id)].add((tp[0], tp[1]))
#     # print(str(len(edges)) + " = len(edges)")
#     return edges

# load edges set version
def load_edges(data_dir, predictor):
    edges = set()
    # count = 0
    for line in open(os.path.join(data_dir, 'link.txt')):
        # line = [i for i in line.split() if i in predictor.uname2uid]
        # print(line)
        line = [i for i in line.split('\t')]
        doc_id = predictor.uname2uid[line[0]]
        ref_id = predictor.uname2uid[line[1]]
        for tpl in line[2:-1]:
            tp = tpl.split(' ')
            edges.add((doc_id, ref_id, int(tp[0]), int(tp[1])))
        # if count < 10:
        #     print ((doc_id, ref_id, int(tp[0]), int(tp[1])))
        #     count += 1
    print(str(len(edges)) + " = len(edges)")
    return edges


def prdict_edges(predictor, edges, tag):
    scores = []
    count = 0
    # for edge in random.sample(edges, num):
    for edge in edges:
        scores.append(predictor.link_predict(*edge))
        if count % 100000 == 0:
            print(datetime.datetime.now(), tag, count, scores[-1])
            sys.stdout.flush()
        count += 1
    return scores


def get_neg_edges(edges, predictor, max_uid, num):
    neg_edges = []
    for i in range(num):
        while True:
            from_user = random.randint(0, max_uid)
            to_user = random.randint(0, max_uid)
            from_time = random.randint(1990, 2016)
            to_time = random.randint(1990, 2016)
            # if isinstance(predictor, MAGICPredictor):
            #     if predictor.label[from_user][1] == predictor.label[to_user][1]:
            #         continue
            #     elif predictor.label[from_user][1] > predictor.label[to_user][1]:
            #         from_user, to_user = to_user, from_user
            if (from_user, to_user, from_time, to_time) not in edges and (to_user, from_user, to_time, from_time) not in edges:
                break
        neg_edges.append((from_user, to_user, from_time, to_time))
    return neg_edges


def load_data(args):
    model2predictor = {
        'bigclam': BIGCLAMPredictor,
        'cdot': CDOTPredictor,
    }
    predictor = model2predictor[args['model']]()
    data_dir = os.path.join(args['root'], args['dataset_path'], args['mode'], args['conference'])
    # load data
    predictor.load_data(data_dir)
    ujson.dump(predictor.uname2uid, open('uname2uid.json', 'w'))
    global edges
    edges = load_edges(data_dir, predictor)
    # ujson.dump(edges, open('edges.json', 'w'))
    pos_edges = random.sample(edges, int(len(edges) * 0.1))
    neg_edges = get_neg_edges(edges, predictor, len(predictor.uname2uid) - 1, int(len(edges) * 0.1))
    print(datetime.datetime.now(), 'load edges done')
    sys.stdout.flush()
    return pos_edges, neg_edges


def predict(args):
    print(datetime.datetime.now(), args)
    sys.stdout.flush()
    args['data_dir'] = os.path.join(args['root'], args['dataset_path'])
    model2result_prefix = {
        'bigclam': os.path.join(args['root'], 'res', args['model'], args['mode'], args['conference']),
        'cdot': os.path.join(args['root'], 'res', args['model'], args['mode'], args['conference'], args['version']),
    }
    args['result_prefix'] = model2result_prefix[args['model']].format(**args)
    model2score_prefix = {
        'bigclam': os.path.join(args['root'], 'measure', args['model'], args['mode'], args['conference'], args['exp']),
        'cdot': os.path.join(args['root'], 'measure', args['model'], args['mode'], args['conference'], args['version'], args['exp']),
    }
    args['score_prefix'] = model2score_prefix[args['model']].format(**args)
    mkdir_if_not_exists(args['score_prefix'])
    print ("added args: ", args)
    # if not (os.path.exists(os.path.join(args['score_prefix'], args['n'] + '.pos.txt')) and os.path.exists(os.path.join(args['score_prefix'], args['n'] + '.neg.txt'))):
    tmp_filename = genearate_tmp_filename(ujson.dumps(args))
    ujson.dump(args, open(tmp_filename, 'w'))
    print ("tempfilename", tmp_filename)
    subprocess.run('python predict_one.py %s' % tmp_filename, shell=True)
    os.remove(tmp_filename)
    pos_score = [float(line) for line in open(os.path.join(args['score_prefix'], args['n'] + '.pos.txt'))]
    neg_score = [float(line) for line in open(os.path.join(args['score_prefix'], args['n'] + '.neg.txt'))]
    auc = roc_auc_score([1] * len(pos_score) + [0] * len(neg_score), pos_score + neg_score)
    print(datetime.datetime.now(), 'auc: ', auc)
    sys.stdout.flush()

    args['score'] = auc
    return args


if __name__ == '__main__':
    print (sys.argv)
    dataset_path = sys.argv[1]
    model = sys.argv[2]
    mode = sys.argv[3]
    conference = sys.argv[4]
    version = sys.argv[5]

    community_count = [
        100,
    ]

    exp = 'link_pred'
    root = os.path.abspath(os.path.join('..', '..'))
    pos_edges, neg_edges = load_data({'exp': exp, 
                                    'root': root, 
                                    'model': model, 
                                    'dataset_path': dataset_path, 
                                    'mode': mode,
                                    'conference': conference})
    ujson.dump(pos_edges, open('pos_edges.json', 'w'))
    del pos_edges
    ujson.dump(neg_edges, open('neg_edges.json', 'w'))
    del neg_edges
    result = []
    to_pred = []
    for cc in community_count:
        to_pred.append({'exp': exp, 
                        'root': root, 
                        'model': model, 
                        'dataset_path': dataset_path, 
                        'cc': cc, 
                        'n': 'final',
                        'mode': mode,
                        'conference': conference,
                        'version': version})
        # predict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final'})
        gc.collect()
        # if 'MAGIC' in model:
        #     for n in range(0, 100, 10):
        #         to_pred.append({'exp': exp, 
        #                         'root': root, 
        #                         'model': model, 
        #                         'dataset_path': dataset_path, 
        #                         'cc': cc, 
        #                         'n': '%05d' % n,
        #                         'mode': mode,
        #                         'conference': conference})
        #         # predict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': '%04d' % n})
    result += Pool(6).map(predict, to_pred, chunksize=1)
    pickle.dump(result, open('result_batch.pkl', 'wb'))
