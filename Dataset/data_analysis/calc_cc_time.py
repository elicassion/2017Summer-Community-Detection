import numpy as np
import os
from math import log, exp
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler
import sys

class Predictor(object):

    def __init__(self, data_dir, result_dir):
        super(predictor, self).__init__()
        # self.data_dir = data_dir
        # self.result_prefix = result_prefix
        # self.load()
        self.load_data(data_dir)
        self.load_result(result_dir)

    def load_data(self, data_dir):
        self.uname2uid = {}
        for line in open(os.path.join(data_dir, 'links.txt')):
            line = line.strip().split('\t')
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)
        for line in open(os.path.join(data_dir, 'del_links.txt')):
            line = line.strip().split('\t')
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)
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


    def calc_error(self, x, y):
        return abs(x-y)/(2016-1980)

    def calc_min_error(self, p_t2, true_t2, used_true_t2, toleration):
        min_e = 99999
        min_e_t2 = None
        for t2 in true_t2.keys():
            if t2 in used_true_t2:
                continue
            calc_e = self.calc_error(p_t2, t2)
            if calc_e < min_e:
                min_e = calc_e
                min_e_t2 = t2
        return min_e, min_e_t2

    def time_predict(self, from_user, to_user, from_time, to_time, predict_mode, toleration):
        # TODO: mode
        # map: no use of toleration
        # direct: use toleration to compare
        # maybe else~

        
        if predict_mode == 'nlog':
            nlog = np.sum(self.f[from_user]*self.f[to_user]*\
                            norm.pdf(from_time, self.mu[from_user], self.sigma[from_user])*\
                            norm.pdf(to_time, self.mu[to_user], self.sigma[to_user]))
            # print ('Nlog: ', nlog)
            # if nlog < 1e-50:
            #     return 1000
            result = - log(1 - exp(-nlog) + sys.float_info.min)
            return result
        else:
            uvt1 = (from_user, to_user, from_time)
            true_t2 = self.uvt1_rec[uvt1]
            true_t2_st = sorted(true_t2.items(), key = lambda item:item[1], reverse = True)
            true_t2 = {}
            for item in true_t2_st:
                true_t2[item[0]] = item[1]
            predict_p = {}
            for t in range(1980, 2017):
                result = 0
                result = np.sum(self.f[from_user]*self.f[to_user]*\
                                norm.pdf(from_time, self.mu[from_user], self.sigma[from_user])*\
                                norm.pdf(t, self.mu[to_user], self.sigma[to_user]))
                result = 1 - exp(-result)
                predict_p[t] = result
            if predict_mode == 'map':
                # st_p = sorted(predict_p.items(), key = lambda item:item[1], reverse = True)
                p_keys = [item[0] for item in predict_p]
                p_values = [item[1] for item in predict_p]
                # min max norm
                mmnorm = MinMaxScaler()
                p_values = mmnorm.fit_transform(np.array(p_values).reshape((-1,1))).reshape(37).tolist()
                accumulate_p = 0
                sum_freq = 0
                for t2, freq in true_t2.items():
                    sum_freq += freq
                    accumulate_p += p_values[p_keys.index(t2)] * freq
                accumulate_p = accumulate_p / sum_freq
                return accumulate_p
            if predict_mode == 'topk':
                st_p = sorted(predict_p.items(), key = lambda item:item[1], reverse = True)
                st_p_keys = [item[0] for item in st_p]
                st_p_values = [item[1] for item in st_p]
                mmnorm = MinMaxScaler()
                st_p_values = mmnorm.fit_transform(np.array(st_p_values).reshape((-1,1))).reshape(37).tolist()
                result = 0
                sum_freq = 0
                for t2, freq in true_t2.items():
                    sum_freq += freq
                used_true_t2 = set()
                for i in range(len(true_t2)):
                    p_t2 = st_p_keys[i]
                    min_error, min_e_t2 = self.calc_min_error(p_t2, true_t2, used_true_t2, toleration)
                    # print (min_error, min_e_t2)
                    used_true_t2.add(min_e_t2)
                    if min_error <= toleration:
                        result += 1 * true_t2[min_e_t2]
                result = result / sum_freq
                return result

data_dir = os.path.join('..', 'data', 't_cite', 'AAAI')
result_dir = os.path.join('res', 'AAAI')
predictor = Predictor(data_dir, result_dir, 287)
