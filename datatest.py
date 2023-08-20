import Vote.vote_rbpl as vote
import Vote.analyzer as analyzer
import Vote.judger as vote_judger
import secureVote.judger as secu_judger
import parameters
import json
import random
import numpy as np
from alive_progress import alive_bar
SP = "./se_result"
VP = "./ns_result"
LOW_K = 6
MAX_K = 200
LOW_ep = 0.08
MAX_ep = 0.09
MAX_EX = 200
# import Vote.Beacon as Beacon
# EP = vote.parameters.EPISLON
# MAX_SLOT = vote.parameters.MAX_SLOT

def return_result(result):
    result_list = {"CP_k":parameters.CP_K, "EP":parameters.EPISLON, 
        "SEED":parameters.SEED, "RESULT":result}
    return result_list
def Statistics(result):
    res = []
    for ele in result:
        res.append(ele["RESULT"])
    vote_judge_ele = []
    for ele in res:
        if ele["vote_sec"] == "right":
            vote_judge_ele.append(1)
        else:
            vote_judge_ele.append(0)
    vote_acc = sum(vote_judge_ele)/len(vote_judge_ele)
    chain_judge_ele = []
    for ele in res:
        if ele["chain_sec"] == "right":
            chain_judge_ele.append(1)
        else:
            chain_judge_ele.append(0)
    chain_acc = sum(chain_judge_ele)/len(vote_judge_ele)
    result_list = {"CP_k":parameters.CP_K, "EP":parameters.EPISLON, "MAX_SLOT":parameters.MAX_SLOT,
        "chain_acc":chain_acc, "vote_acc":vote_acc}
    return result_list


def start_exe():
    vote_list = []
    sec_list = []
    with alive_bar(len(range(110))) as bar:
        for k in range(LOW_K, MAX_K, 1):
            parameters.CP_K = k
            parameters.EPOCH = 4*parameters.CP_K+1
            for ep in np.arange(LOW_ep, MAX_ep, 0.01):
                bar()
                parameters.EPISLON = ep
                vote_result = []
                sec_result = []
                for i in range(0, MAX_EX):
                    # parameters.SEED = random.randint(0, 500)
                    parameters.SEED += 1
                    parameters.SEED = parameters.SEED%5000
                    vote_judger.parameters = parameters
                    secu_judger.parameters = parameters
                    # print(vote_judger.parameters)
                    ans1 = vote_judger.main()
                    vote_result.append(return_result(ans1))
                    # print(return_result(ans1))
                    ans2 = secu_judger.main()
                    # print(return_result(ans2))
                    sec_result.append(return_result(ans2))
                sec_list.append(Statistics(sec_result))
                vote_list.append(Statistics(vote_result))
    print(sec_list)
    print("-------------------")
    print(vote_list)
    with open(SP, "w") as f:
        f.write(json.dumps(sec_list))
    with open(VP, "w") as f:
        f.write(json.dumps(vote_list))



def main():



    start_exe()

if __name__ == '__main__':
    main()