# Secure Trajectory Publication in Untrusted Environments: A Federated Analytics Approach

This project is abbreviated as FASTPub.

## Abstract
The increasing awareness of privacy and the adoption of data regulations challenge the traditional trajectory publication framework in which a trusted server has access to the raw data from mobile clients. In the new untrusted environment, the clients call for much stronger data privacy preservation locally without sharing their raw data. Based on the emerging paradigm of federated analytics, we propose a Federated Analytics-based Secure Trajectory PUBlication (FASTPub) mechanism to operate in such untrusted environments. Compared with existing local differential privacy (LDP) methods, FASTPub guarantees LDP and loss-bounded $k$-anonymity simultaneously with greatly improved data utility. Specifically, FASTPub works interactively between the server and clients and iteratively builds up the trajectory without exposing raw data. Sampled clients only respond to selected trajectory fragments with randomized answers to preserve privacy as much as possible. The server then intelligently aggregates these randomized responses leveraging the intrinsic Apriori property and a Markov independent assumption of trajectory data to guide further iterations. Extensive experiments on synthetic and real-world datasets on two downstream tasks demonstrate that FASTPub gains a remarkably improved data utility compared to the existing state-of-the-art solutions.

## Features
- functionality of FASTPub on a simulated trajectory publication environment
- two trajectory datasets: MSNBC (real-world network browsing trajectory) and Oldenburg (synthetic mobility trajectory)
- two benchmarks: SFP and TrieHH
- two downstream tasks and corresponding evaluation metrics: frequent pattern mining (F1 score), and count query (relative error)
- multiprocessing in simulation

## Installation
```
python==3.8
numpy==1.20.1
multiprocess==0.70.11.1
```

## Preparation of datasets and groundtruths (statistics on the trajectory data for evaluation)

We provide the datasets and groundtruth data in https://drive.google.com/file/d/1MdMuOE8jEWjuxCmUQyUKvNq7VTx5rdPK/view?usp=sharing

You can download the folders "./data" and "./save" and place them in the project root directory.

### You can also prepare those by yourself

To prepare the datasets, you can write datastructures like those in "./models/DataSet.py". Note that you should implement two structures: one is the local data in one client (like **class Trajectory**). The other is the global dataset of all clients (like **class DataSet**). All the methods present in "./models/DataSet.py" should be implemented. After that, you need to pickle the latter structure and read them in "./main.py"

The groundtruth data is required to calculate the F1 score and relative error. To prepare the groundtruths, you can run the codes with --mode==groundtruth, and the ground truth patterns will be automatically saved. Note that the save includes all fragments with length --l that exceed the anonymity requirement (--k) along with their counts. The save can work for all future runs with higher frequency and identical trajectory length, e.g., if you have run the code with "--mode==groundtruth --dataset=msnbc --k=100000 --l=3", you can simply run "--mode==fastpub --dataset=msnbc --k=200000 --l=3" and calculate the metrics properly (but you cannot run other fragment length without the corresponding groundtruth generation).

## Run the code

We present some lines to reproduce some of our experiment results.

Run FASTPub on MSNBC dataset, with fragment length $l=3$ and anonymity value $k=100,000$

```
%run main.py --dataset=msnbc --mode=fastpub  --k=100000 --l=3 --min_length=3  --num_participants=0.2 --process=14 --duplicate=100 --epsilon=10 --c_max=5
```

Run SFP on MSNBC dataset, with fragment length $l=4$ and anonymity value $k=300,000$

```
%run main.py --dataset=msnbc --mode=sfp --k=300000 --l=4 --min_length=3  --num_participants=0.8 --process=14 --duplicate=100 --sfp_threshold=80 --epsilon=10
```

Run TrieHH on Oldenburg dataset, with fragment length $l=5$ and anonymity value $k=500,000$
```
%run main.py --dataset=oldenburg --mode=triehh  --k=500000 --l=5 --min_length=3  --num_participants=0.2 --process=14 --duplicate=1 --epsilon=10 --round_threshold=5
```


## Citation format

Z. Wang, Y. Zhu, D. Wang, and Z. Han, "Secure Trajectory Publication in Untrusted Environments: A Federated Analytics Approach," In *IEEE Transactions on Mobile Computing (TMC)*, 2022.

```
@inproceedings{wang2022fastpub,
  title={Secure Trajectory Publication in Untrusted Environments: A Federated Analytics Approach},
  author={Wang, Zibo and Zhu, Yifei and Wang, Dan and Han, Zhu},
  booktitle={IEEE Transactions on Mobile Computing (TMC)},
  year={2022}
}
```
