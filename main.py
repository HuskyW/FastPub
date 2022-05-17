from LoadData import loadMsnbc
from utils.Options import args_parser
import pickle
from models.GroundTruth import groundTruth, groundTruthFromConfig
from models.Handlers import FastPubHandler
from models.Triehh import TriehhHandler
from utils.Naming import GroundTruthPickleName, SupportCountPickleName
from models.SFP import SfpHandler
from utils.Print import printLog
from models.Database import Database
import os
import math
import numpy as np


def ckeckWithGroundTruth(result,truth,killed):
    tp = 0
    for frag in result:
        if frag in truth:
            tp += 1
    precision = tp/len(result)
    recall = tp/len(truth)
    f1 = 2*(precision*recall) / (precision + recall)
    print("Precision: %.2f; Recall: %.2f; F1: %.2f" % (precision,recall,f1))

    badkill = 0
    for frag in killed:
        if frag not in truth:
            badkill += 1
    print("Bad kill: %d / %d (%.4f)" % (badkill , len(killed), badkill / len(killed)))

    return precision, recall

def getGroundTruth(args):
    pickleName = GroundTruthPickleName(args)
    scName = SupportCountPickleName(args)

    with open(scName,'rb') as fp:
        sc_rec = pickle.load(fp)
        if sc_rec['k'] > (args.k/args.duplicate):
            print("Support count record invalid")
            exit(0)
        data = sc_rec['data']
        ground_truth = [i[0] for i in data if i[1] >= (args.k/args.duplicate)]
        ground_truth_rec = [(i[0],i[1]*args.duplicate) for i in data if i[1] >= (args.k/args.duplicate)]
        return ground_truth, ground_truth_rec
    print("Ground truth not generated yet")
    exit(0)

def queryError(db,truth):
    error_list = []
    for f,true_count in truth:
        noisy_count = db.query(f)
        error = abs(noisy_count-true_count)/true_count
        error_list.append(error)
        # print(f)
        # print(true_count)
        # print(noisy_count)
        # print(error)
    avg_error = sum(error_list)/len(error_list)
    med_error = np.median(error_list)
    print("Average query error: %.2f" % avg_error)
    print("Median query error: %.2f" % med_error)
    return avg_error,med_error


def queryErrorRef(db,truth,fragment):
    error_list = []
    for f,true_count in truth:
        if f not in fragment:
            continue
        noisy_count = db.query(f)
        error = abs(noisy_count-true_count)/true_count
        error_list.append(error)
    avg_error = sum(error_list)/len(error_list)
    med_error = np.median(error_list)
    print("Average query error on mined patterns: %.2f" % avg_error)
    print("Median query error on mined patterns: %.2f" % med_error)
    return avg_error

if __name__ == '__main__':
    args = args_parser()
    if args.dataset == 'msnbc':
        if args.load_pickle is True:
            with open('data/msnbc.pickle','rb') as fp:
                dataset = pickle.load(fp)
        else:
            dataset = loadMsnbc(dump=args.write_pickle,minLength=args.min_length,maxLength=args.max_length)
    elif args.dataset == 'zipf':
        with open('data/zipf.pickle','rb') as fp:
            dataset = pickle.load(fp)
        with open('data/zipf_config.pickle','rb') as fp:
            config = pickle.load(fp)
    elif args.dataset == 'oldenburg':
        with open('data/oldenburg.pickle','rb') as fp:
            dataset = pickle.load(fp)
    else:
        print("Bad argument: dataset")

    #dataset = [[1,4,7,8,3,5]]

    args.orig_num_participents = args.num_participants
    if args.orig_num_participents <= 1:
        args.num_participants = int(math.floor(dataset.get_traj_num() * args.duplicate * args.orig_num_participents) )

    if args.mode == 'groundtruth':
        if args.dataset == 'zipf':
            fragments = groundTruthFromConfig(config,args)
            print(fragments)
        else:
            fragments = groundTruth(dataset,args)
            print(fragments)
    else:  
        if args.mode == 'fastpub':
            handler = FastPubHandler(args,dataset)
        elif args.mode == 'triehh':
            handler = TriehhHandler(args,dataset)
        elif args.mode == 'sfp':
            handler = SfpHandler(args,dataset)
        fragments, db, killed = handler.run()
        # if args.verbose:
        #     for frag in fragments:
        #         print(frag)


    if args.dataset == 'zipf':
        ground_truth = groundTruthFromConfig(config,args)
    elif args.dataset == 'msnbc' or args.dataset == 'oldenburg':
        ground_truth, ground_truth_rec = getGroundTruth(args)
    print("Num. ground truth: %d" % len(ground_truth))
    if len(fragments) > 0:
        precision, recall = ckeckWithGroundTruth(fragments,ground_truth,killed)
        avg_error,med_error = queryError(db,ground_truth_rec)
        queryErrorRef(db,ground_truth_rec,fragments)
    else:
        print("No fragment published")
        precision = -1.0
        recall = 0.0
        avg_error = -1.0
        med_error = -1.0

    if args.mode != 'groundtruth':
        log = printLog(args,(precision,recall,avg_error,med_error))
        with open('./save/log','a') as fp:
            fp.write(log)


