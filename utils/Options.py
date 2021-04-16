import argparse

def args_parser():
    parser = argparse.ArgumentParser()
    # Basic params
    parser.add_argument('--l', type=int, default=3, help="target fragment length")
    parser.add_argument('--k', type=int, default=50, help="threshold of k-anonymity")
    parser.add_argument('--xi', type=float, default=0.25, help="allowed error rate for k-anonymity")
    parser.add_argument('--epsilon', type=float, default=10.0, help="param of LDP")
    parser.add_argument('--num_participants', type=int, default=300000, help="number of participating clients")
    parser.add_argument('--mode', type=str, default='fastpub', help="mode: groundtruth || fastpub")

    # Advanced params
    parser.add_argument('--c_max', type=int, default=10, help="maximum candidates assigned to one client")
    parser.add_argument('--softk', action='store_true', help='loosy k parameter thresholding')
    parser.add_argument('--admit_threshold', type=int, default=-1, help="Number of admit fragments in each round, -1: disable thresholding")

    # Settings
    parser.add_argument('--dataset', type=str, default='msnbc', help="msnbc || zipf")
    parser.add_argument('--load_pickle', action='store_true', help='read dataset form pickle file')
    parser.add_argument('--write_pickle', action='store_true', help='store dataset into pickle file, do not work when --load_pickle is activated')


    parser.add_argument('--min_length', type=int, default=None, help="minimal length of each trajectory")
    parser.add_argument('--max_length', type=int, default=None, help="maximal length of each trajectory")
    parser.add_argument('--verbose', action='store_true', help='verbose print')

    parser.add_argument('--process', type=int, default=0, help="number of worker processes, 0: single process")


    args = parser.parse_args()
    return args