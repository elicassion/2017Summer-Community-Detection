import numpy as np
import os
from math import exp
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

class predictor(object):

    def __init__(self):
        super(predictor, self).__init__()
        # self.data_dir = data_dir
        # self.result_prefix = result_prefix
        # self.load()

    def load_data(self, data_dir):
        self.uname2uid = {}
        self.uvt1_rec = {}
        for line in open(os.path.join(data_dir, 'link.txt')):
            line = line.split('\t')
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)
            doc_id = self.uname2uid[line[0]]
            ref_id = self.uname2uid[line[1]]
            for tpl in line[2:-1]:
                tp = tpl.split(' ')
                t1 = int(tp[0])
                t2 = int(tp[1])
                uvt1 = (doc_id, ref_id, t1)
                # Currently ignore the condition when it has multiple t2
                if uvt1 not in self.uvt1_rec.keys():
                    self.uvt1_rec[uvt1] = set()
                self.uvt1_rec[uvt1].add(t2)
        print ("load data done.")

    def load_result(self, result_prefix, n, uname2uid, cc):
        # print (os.path.join(result_prefix, n + '.f_mu_sigma.txt'))
        resf = open(os.path.join(result_prefix, n + '.f_mu_sigma.txt'), 'r')
        res = resf.read()
        # print (res)
        lines = res.split('\n')
        au_num = len(uname2uid)
        # L0=19
        self.f = np.zeros([au_num, cc])
        # self.mu = np.zeros([au_num, cc])
        self.mu = np.linspace(2008, 2008, au_num*cc).reshape((au_num, cc))
        self.sigma = np.ones([au_num, cc])
        for au_id, line in enumerate(lines[1:-1]):
            items = line.split('\t')
            au = items[0]
            edges = items[1]
            if edges is not '[]':
                edges = edges.replace('[', '').replace(']', '').split(' ')
            else:
                continue
            for edge in edges[:-1]:
                edge = edge.replace('(', '').replace(')', '')
                tpl = edge.split(',')
                comm_id = int(tpl[0])
                self.f[au_id][comm_id] = float(tpl[1])
                self.mu[au_id][comm_id] = float(tpl[2])
                self.sigma[au_id][comm_id] = float(tpl[3])
                # print (tpl)
        self.U = au_num
        self.C = cc
        print ("load result done.")
        # print (np.dot(self.f[0], self.f[1]))
        print (np.dot(norm.pdf(1994, self.mu[0], self.sigma[0]), norm.pdf(1998, self.mu[1], self.sigma[1])))

    def time_predict(self, from_user, to_user, from_time, to_time, toleration):
        # TODO: mode
        # topk: no use of toleration
        # direct: use toleration to compare
        # maybe else~
        time_pred_mode = 'topk'
        uvt1 = (from_user, to_user, from_time)
        true_t2 = self.uvt1_rec[uvt1]
        predict_p = {}
        for t in range(1980, 2017):
            result = 0
            for i in range(self.f.shape[1]):
                result += self.f[from_user][i] * self.f[to_user][i] * \
                        norm.pdf(from_time, self.mu[from_user][i], self.sigma[from_user][i]) * \
                        norm.pdf(t, self.mu[to_user][i], self.sigma[to_user][i])
            result = 1 - exp(-result)
            predict_p[t] = result
        print ("predict_p:", predict_p)
        if time_pred_mode is 'topk':
            st_p = sorted(predict_p.items(), key = lambda item:item[1], reverse = True)
            st_p_keys = [item[0] for item in st_p]
            st_p_values = [item[1] for item in st_p]
            # min max norm
            mmnorm = MinMaxScaler()
            st_p_values = mmnorm.fit_transform(np.array(st_p_values)).tolist()
            # print ("st_p:", st_p_keys)
            # print (st_p_values)
            # print (true_t2)
            accumulate_p = 0
            for t2 in true_t2:
                accumulate_p += st_p_values[st_p_keys.index(t2)]
            accumulate_p = accumulate_p / len(true_t2)
            return accumulate_p
        else:
            return 0
