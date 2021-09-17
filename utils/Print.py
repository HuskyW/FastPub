import time

def printRound(i):
    print('==================================')
    print('             Round %d             ' % i)
    print('==================================')

def printLog(args,performance):
    timestemp = str(time.strftime('%Y.%m.%d-%H:%M:%S',time.localtime(time.time())))
    record = timestemp + ';'
    record += '%s;' % str(args.dataset)
    record += '%s;' % str(args.mode)
    record += 'precision=%.4f;' % performance[0]
    record += 'recall=%.4f;' % performance[1]
    record += 'l=%d;' % args.l
    record += 'k=%d;' % args.k
    record += 'dup=%d;' % args.duplicate
    if args.orig_num_participents > 1:
        record += 'm=%d;' % int(args.orig_num_participents)
    else:
        record += 'm=%.2f;' % float(args.orig_num_participents)

    if args.mode == 'fastpub':
        record += 'epsilon=%.1f;' % args.epsilon
        record += 'c_max=%d;' % args.c_max
        record += 'xi=%.2f;' % args.xi
        record += 'markov=%.2f' % args.markov_filter
    if args.mode == 'sfp':
        record += 'epsilon=%.1f;' % args.epsilon
        record += 'sfp_threshold=%d;' % args.sfp_threshold
        record += 'k_cut=%.2f' % args.k_cut
    if args.mode == 'triehh':
        record += 'round=%d' % args.round_threshold
    
    record += '\n'
    return record