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
        self.docs = {}
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

        if not os.path.exists(os.path.join(vis_dir, 'docs.json')):
            for line in open(os.path.join(data_dir, 'docs.txt')):
                line = line.strip().split('\t')
                if line[0] not in self.docs:
                    self.docs[line[0]] = {}
                if line[1] not in self.docs[line[0]]:
                    self.docs[line[0]][line[1]] = []
                self.docs[line[0]][line[1]].append(line[2])
            ujson.dump(self.docs, open('docs.json', 'w'))
            print ("Load Docs Done.")
        else:
            self.docs = ujson.loads(open(os.path.join(vis_dir, 'docs.json'), 'r').read())
            print ("Load Docs Done.")


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
    def show_community_time(self):
        comm_t = []
        for t in range(1955, 2017):
            comm = [0 for i in range(self.cc)]
            # for i in range(self.cc):
            #     comm[i] = 0
            for uname in self.uname2uid.keys():
                uid = self.uname2uid[uname]
                f = self.f[uid]
                mu = self.mu[uid]
                sigma = self.sigma[uid]
                p_v = f*norm.pdf(t, mu, sigma).tolist()
                mmnorm = MinMaxScaler()
                st_v = mmnorm.fit_transform(np.array(p_v).reshape((-1,1))).reshape(self.cc)
                for i in range(self.cc):
                    if st_v[i] > 0.3 and p_v[i] > 1e-5:
                        # comm[i].add(uname)
                        comm[i] += 1
            print ("Year: %d" % t)
            comm_t.append(comm)
        comm_vis_filename = os.path.join(self.vis_dir, "comm_vis.csv")
        np.savetxt(comm_vis_filename, np.array(comm_t), fmt='%d', delimiter=',')
        
    def vis_comm(self):
        if not os.path.exists(os.path.join(self.vis_dir, 'draw_comm_data')):
            os.makedirs(os.path.join(self.vis_dir, 'draw_comm_data'))
        comm_t = []
        for t in range(1955, 2017):
            print ("Year: %d" % t)
            comm = [0 for i in range(self.cc)]
            au_comm = []
            for uname in self.uname2uid.keys():
                uid = self.uname2uid[uname]
                f = self.f[uid]
                mu = self.mu[uid]
                sigma = self.sigma[uid]
                p_v = f*norm.pdf(t, mu, sigma).tolist()
                p_vd = {}
                for i in range(self.cc):
                    p_vd[i] = p_v[i]
                s_vt = sorted(p_vd.items(), key = lambda item:item[1], reverse=True)
                s_v = s_vt[:2]
                sm = s_v[0][1] + s_v[1][1]
                if sm < 1e-10:
                    r_v = [(s_v[0][0], 0.5), (s_v[1][0], 0.5)]
                else:
                    r_v = [(s_v[0][0], s_v[0][1]/sm), (s_v[1][0], s_v[1][1]/sm)]
                au_comm.append(r_v)
                if s_v[0][1] > 1e-5:
                    comm[s_v[0][0]] += 1
                if s_v[1][1] > 1e-5:
                    comm[s_v[1][0]] += 1
            comm_t.append(comm)
            
            comm_vis_file = open(os.path.join(self.vis_dir, 'draw_comm_data', "comm_vis_%d.txt" % t), "w")
            for item in au_comm:
                comm_vis_file.write("%d %.3f\t%d %.3f\n" % (item[0][0], item[0][1], item[1][0], item[1][1]))
            comm_vis_file.close()
        comm_vis_filename = os.path.join(self.vis_dir, "comm_vis.csv")
        np.savetxt(comm_vis_filename, np.array(comm_t), fmt='%d', delimiter=',')

    def vis_topic(self):
        if not os.path.exists(os.path.join(self.vis_dir, 'comm_topic')):
            os.makedirs(os.path.join(self.vis_dir, 'comm_topic'))
        comm = [[] for i in range(self.cc)]
        for uname in self.uname2uid.keys():
            uid = self.uname2uid[uname]
            f = self.f[uid]
            mu = self.mu[uid]
            sigma = self.sigma[uid]
            for year in self.docs[uname].keys():
                t = int(year)
                p_v = f*norm.pdf(t, mu, sigma).tolist()
                p_vd = {}
                for i in range(self.cc):
                    p_vd[i] = p_v[i]
                s_vt = sorted(p_vd.items(), key = lambda item:item[1], reverse=True)
                cc = s_vt[0][0]
                for title in self.docs[uname][year]:
                    comm[cc].append(title)
        for ccnum, titles in enumerate(comm):
            f = open(os.path.join(self.vis_dir, 'comm_topic', '%d.txt' % ccnum), 'w')
            for title in titles:
                f.write("%s\n" % title)
            f.close()

set_type = 'new_big_data'
data_dir = os.path.join('..', 'data', 'test_fos', set_type)
result_dir = os.path.join('..', 'res', 'cdot', 'test_fos', set_type, 'bd_083100')
vis_dir = os.path.join('res', set_type)
predictor = Predictor(data_dir, result_dir, vis_dir, 25)

# predictor.show_community_time()
# predictor.vis_comm()
predictor.vis_topic()
