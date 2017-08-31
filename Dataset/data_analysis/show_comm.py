import numpy as np
import os
import math
from math import log, exp
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler
import sys
import ujson

def potionScaler(l):
    return l / np.sum(l)


class Predictor(object):

    def __init__(self, data_dir, result_dir, vis_dir, cc):
        super(Predictor, self).__init__()
        self.data_dir = data_dir
        self.result_dir = result_dir
        self.vis_dir = vis_dir
        self.cc = cc
        self.uname2uid = {}
        self.links = set()
        self.min_time = 1955
        self.max_time = 2016
        self.load_data(data_dir)
        self.load_result(result_dir)
        
        


    def load_data(self, data_dir):
        if not os.path.exists(os.path.join(vis_dir, 'uname2uid.json')):
            for line in open(os.path.join(data_dir, 'links.txt')):
                line = line.strip().split('\t')
                if line[0] not in self.uname2uid:
                    self.uname2uid[line[0]] = len(self.uname2uid)
                if line[1] not in self.uname2uid:
                    self.uname2uid[line[1]] = len(self.uname2uid)
            ujson.dump(self.uname2uid, open('uname2uid.json', 'w'))
            print ("Load Data Done.")
        else:
            self.uname2uid = ujson.loads(open(os.path.join(vis_dir, 'uname2uid.json'),"r").read())
            print ("Load Data Done.")


    def load_result(self, result_dir):
        resf = open(os.path.join(result_dir, 'final.f_mu_sigma.txt'), 'r')
        res = resf.read()
        lines = res.split('\n')
        au_num = len(self.uname2uid)
        self.f = np.zeros([au_num, self.cc])
        self.mu = np.linspace(2008, 2008, au_num*self.cc).reshape((au_num, self.cc))
        self.sigma = np.ones([au_num, self.cc])
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
        self.U = au_num
        self.C = self.cc
        print ("Load Result Done.")
        # print (np.dot(self.f[0], self.f[1]))
        # print (np.dot(norm.pdf(1994, self.mu[0], self.sigma[0]), norm.pdf(1998, self.mu[1], self.sigma[1])))

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
        

    #6, 9, 18
    def show_community_time(self, t):
        comm = {}
        comm[6] = set()
        comm[9] = set()
        comm[18] = set()
        for uname in self.uname2uid.keys():
            uid = self.uname2uid[uname]
            f = self.f[uid]
            mu = self.mu[uid]
            sigma = self.sigma[uid]
            p_values = f*norm.pdf(t, mu, sigma).tolist()
            v = []
            v.append(p_values[6])
            v.append(p_values[9])
            v.append(p_values[18])
            mmnorm = MinMaxScaler()
            st_v = mmnorm.fit_transform(np.array(v).reshape((-1,1))).reshape(3)
            if st_v[0] > 0.3 and v[0] > 1e-5:
                comm[6].add(uname)
            if st_v[1] > 0.3 and v[0] > 1e-5:
                comm[9].add(uname)
            if st_v[2] > 0.3 and v[0] > 1e-5:
                comm[18].add(uname)
        print ("Year: %d" % t)
        print (len(comm[6]), len(comm[9]), len(comm[18]))




data_dir = os.path.join('..', 'data', 'test_fos', 'big_data')
result_dir = os.path.join('..', 'res', 'cdot', 'test_fos', 'big_data', 'bd_083100')
vis_dir = os.path.join('res', 'big_data')
predictor = Predictor(data_dir, result_dir, vis_dir, 34)
for i in range(2000, 2017):
    predictor.show_community_time(i)
