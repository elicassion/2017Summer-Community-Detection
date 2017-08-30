import numpy as np
import os
import math
from math import log, exp
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler
import sys

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
        self.min_time = 99999
        self.max_time = 0
        self.load_data(data_dir)
        self.load_result(result_dir)
        
        


    def load_data(self, data_dir):
        
        for line in open(os.path.join(data_dir, 'links.txt')):
            line = line.strip().split('\t')
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)
            for tpl in line[2:]:
                tp = tpl.split(' ')
                t1 = int(tp[0])
                t2 = int(tp[1])
                self.min_time = min(self.min_time, t1)
                self.min_time = min(self.min_time, t2)
                self.max_time = max(self.max_time, t1)
                self.max_time = max(self.max_time, t2)
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
        

    def show_distribute(self, uname):
        uid = self.uname2uid[uname]
        res_para_file = open(os.path.join(self.vis_dir, "%s_para.txt" % uname), "w")
        # print (self.f[uid])
        # print (self.mu[uid])
        # print (self.sigma[uid])
        f = self.f[uid]
        mu = self.mu[uid]
        sigma = self.sigma[uid]
        for i in f:
            res_para_file.write("%.18e\t" % i)
        res_para_file.write('\n')
        for i in mu:
            res_para_file.write("%.18e\t" % i)
        res_para_file.write('\n')
        for i in sigma:
            res_para_file.write("%.18e\t" % i)
        res_para_file.close()

        dis_file_name = os.path.join(self.vis_dir, "%s_vis.csv" % uname)
        portions = []
        s_portions = []
        for t in range(1955, 2017):
            p_values = f*norm.pdf(t, mu, sigma)
            st_p_values = potionScaler(p_values).tolist()
            portions.append(st_p_values)
            s_portions.append(np.sum(p_values))
        mmnorm = MinMaxScaler()
        # print (s_portions)
        st_sp = mmnorm.fit_transform(np.array(s_portions).reshape((-1,1))).reshape(62)
        # print (st_sp)
        portions = np.array(portions)
        for i in range(34):
            portions[i] *= st_sp[i]
        # print (portions)
        np.savetxt(dis_file_name, portions, fmt='%.7f', delimiter=',')

    def find_nice(self, scope):
        th = 4
        lt = scope[0]
        rt = scope[1]
        nice_list = []
        for uname in self.uname2uid.keys():
            uid = self.uname2uid[uname]
            count = 0
            mu = self.mu[uid]
            for i in mu:
                if i > lt and i < rt and abs(i-2008) > 0.5:
                    count += 1
            if count >= th:
                nice_list.append(uname)
        nice_file = open(os.path.join(self.vis_dir, "nice_%d.txt" % th), "w")
        for i in nice_list:
            nice_file.write("%s\n" % i)
        print ("Nice Person Count: %d" % len(nice_list))




data_dir = os.path.join('..', 'data', 'test_fos', 'big_data')
result_dir = os.path.join('..', 'res', 'cdot', 'test_fos', 'big_data', 'bd_082800')
vis_dir = os.path.join('res', 'big_data')
predictor = Predictor(data_dir, result_dir, vis_dir, 34)
distribute = predictor.show_distribute('8039481B')
# distribute = predictor.show_distribute('80006CCF')
# distribute = predictor.show_distribute('077D8DEE')
# predictor.find_nice((1955, 2017))