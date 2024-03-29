'''
    Handler of FastPub, an FastPubHandler instance an do all works of trajectory publication given the dataset
'''
import abc
from utils.Randomize import *
import math
import numpy as np
from collections import defaultdict
from utils.Candidate import generateCandidates
from utils.Sampling import CandidateSampler
from utils.Print import printRound
import multiprocess
import random
from models.Database import CountingDatabase


class Handler(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def run(self):
        pass


class FastPubHandler(Handler):
    def __init__(self,args,dataset):
        self.args = args
        self.dataset = dataset
        self.orig_traj_num = self.dataset.get_traj_num()
        self.clients_num = self.dataset.get_traj_num() * self.args.duplicate
        self.loc_num = self.dataset.location_num
        self.round = 0
        self.eta = [0] * self.args.l
        self.thres = [0] * self.args.l
        self.c_len = [0] * self.args.l
        self.client_list = []
        self.markov_thres = self.args.markov_filter
        self.markov_record = {}
        for i in range(self.args.duplicate):
            self.client_list.extend(list(range(self.orig_traj_num)))
        random.shuffle(self.client_list)
        
        

    def __sampleClients(self):
        if self.args.one_participation is False:
            res = np.random.choice(self.clients_list,self.args.num_participants,replace=False)
            return res
        res = self.client_list[0:self.args.num_participants]
        self.client_list = self.client_list[self.args.num_participants:len(self.client_list)]
        return res


    def __calculateEta(self):
        epsilon = self.args.epsilon
        return 1/(1 + math.pow(math.e,(epsilon/self.c_len[self.round])))


    def __calculateThres(self,m): # m is times checked by clients for each candidate
        p1 = (self.args.k/self.clients_num)*(1-self.eta[self.round])
        p2 = ((self.clients_num-self.args.k)/self.clients_num) * self.eta[self.round]
        p3 = math.sqrt(-math.log(self.args.xi)/(2*m))
        p_softk = self.args.k/self.clients_num
        
        intrinsic_thres = m*(p1+p2+p3)
        observative_thres = m*(p_softk+p3)

        if self.args.softk is True and self.round != self.args.l-1:
            return observative_thres

        return intrinsic_thres  

    
    def __one_client(self,client_idx,candidates):
        candi_len = len(candidates)
        candi_save = list(candidates)
        response = [0] * candi_len
        for i in range(len(candidates)):
            if self.dataset.checkSubSeq(client_idx,candi_save[i]) is True:
                response[i] = 1
        response = randomBits(response,self.eta[self.round])
        final_response = {}
        for i in range(len(candidates)):
            final_response[candi_save[i]] = response[i]
        return final_response
    
    def __one_round_worker(self,proc_idx,candidates,participents,queue):
        num_milestone = 5
        milestone = math.floor(len(participents)/num_milestone)
        local_support_count = defaultdict(lambda : 0)
        sampler = CandidateSampler(candidates)
        for idx in range(len(participents)):
            if idx > 0 and idx % milestone == 0 and int(idx/milestone) != num_milestone and self.args.verbose:
                print("Worker %2d: %d%% done" % (proc_idx,int(round(idx*100/len(participents)))))
            
            client_idx = participents[idx]
            candis = sampler.sample(self.c_len[self.round])
            res = self.__one_client(client_idx,candis)

            for key,value in res.items():
                local_support_count[key] += value

        queue.put(local_support_count)
        if self.args.verbose:
            print("Worker %2d: all done" % proc_idx)
        return


    def __filterCandidates(self,support_count):
        exceed_k = [key for key,value in support_count.items() if value >= self.thres[self.round]]
        if self.args.admit_threshold < 0 or len(exceed_k) < self.args.admit_threshold:
            return exceed_k
        sc_sorted = sorted(support_count.items(),key=lambda item:item[1],reverse=True)
        res = []
        for i in range(self.args.admit_threshold):
            res.append(sc_sorted[i][0])
        return res

    def __denoiseCount(self,count,average_query,eta):
        freq = count/average_query
        estimate_true_freq = (freq - eta) / (1 - 2 * eta)
        return estimate_true_freq * self.clients_num

    def __markovGuess(self,f):
        list_f = list(f)
        frag1 = tuple(list_f[0:len(f)-1])
        frag2 = tuple(list_f[1:len(f)])
        frag3 = tuple(list_f[1:len(f)-1])
        return self.markov_record[frag1] * self.markov_record[frag2] / self.markov_record[frag3]
        
        

    def run(self):

        db = CountingDatabase(self.args.l,self.args.k,self.clients_num)

        # publish longer fragments
        for fragment_len in range(0,self.args.l):
            self.round = fragment_len
            printRound(fragment_len+1)
            if fragment_len != 0:
                candidates = generateCandidates(fragments)
            else:
                candidates = []
                for i in range(self.loc_num):
                    candidates.append((i,))
            print("%d-fragments: %d candidates after Apriori filter" % (fragment_len+1,len(candidates)))

            killed_fragment = []
            if self.args.markov_filter > 0 and fragment_len >= 2:
                filtered_candidates = []
                for f in candidates:
                    if self.__markovGuess(f) >= self.markov_thres * self.args.k:
                        filtered_candidates.append(f)
                    else:
                        killed_fragment.append(f)
                candidates = filtered_candidates
                print("%d-fragments: %d candidates after Markov filter" % (fragment_len+1,len(candidates)))

            if len(candidates) == 0:
                print('No candidate with length ' + str(fragment_len+1))
                return [], db

            self.c_len[fragment_len] = min(self.args.c_max,len(candidates))
            self.eta[fragment_len] = self.__calculateEta()

            sampler = CandidateSampler(candidates)

            participents = self.__sampleClients()

            support_count = defaultdict(lambda : 0)
            
                
            if self.args.process <= 0:
                for idx in range(len(participents)):
                    if idx % 100000 == 0 and idx > 0 and self.args.verbose:
                        print("%d trajectories checked" % idx)
                    client_idx = participents[idx]
                    candis = sampler.sample(self.c_len[self.round])
                    res = self.__one_client(client_idx,candis)
                    for key,value in res.items():
                        support_count[key] += value
            else:
                mananger = multiprocess.Manager()
                queue = mananger.Queue()
                jobs = []
                workload = math.floor(len(participents)/self.args.process)
                for proc_idx in range(self.args.process):
                    if proc_idx == self.args.process - 1:
                        participents_load = participents[proc_idx*workload:len(participents)]
                    else:
                        participents_load = participents[proc_idx*workload:(proc_idx+1)*workload]
                    p = multiprocess.Process(target=self.__one_round_worker,args=(proc_idx,candidates,participents_load,queue))
                    jobs.append(p)
                    p.start()

                for p in jobs:
                    p.join()
                
                if self.args.verbose:
                    print("Aggregating...")

                results = [queue.get() for j in jobs]

                for res in results:
                    for key,value in res.items():
                        support_count[key] += value

                

            query_per_candi = self.args.num_participants * self.c_len[self.round] /len(candidates)
            print("Candidate avg chance: %.2f" % query_per_candi)
            self.thres[fragment_len] = self.__calculateThres(query_per_candi)

            fragments = self.__filterCandidates(support_count)
            for f in fragments:
                count_estimate = self.__denoiseCount(support_count[f], query_per_candi, self.eta[fragment_len])
                self.markov_record[f] = count_estimate
                db.add_record(f,count_estimate)


            print("eta: %.3f" % self.eta[fragment_len])
            print("thres: %.2f" % self.thres[fragment_len])
            print("%d-fragments: %d admitted" % (fragment_len+1,len(fragments)))

        return fragments, db, killed_fragment
                
                





