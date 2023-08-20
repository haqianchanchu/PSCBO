
import secureVote.parameters as parameters
import secureVote.Beacon as Beacon

# import numpy as np
USER_NUMBER = parameters.USER_NUMBER
MAX_OUTPUTIP = parameters.MAX_OUTPUTIP
MAX_INPUTIP = parameters.MAX_INPUTIP
R = parameters.EPOCH
CP_K = parameters.CP_K
MAX_SLOT = parameters.MAX_SLOT
EP = parameters.EPISLON
VOTELEN = 2*CP_K
VOTESPACE = R
class Tree():
    """docstring for tree"""
    def __init__(self):
        pass
    def vote_judge(self):
        for i in range(0, MAX_SLOT-CP_K,1):
            # print("----------------------")
            # print(CP_K)
            value = 0
            for j in range(0, VOTELEN):
                sl = i+j
                if Beacon.select(sl) == Beacon.corrupt:
                    value -= 1
                else:
                    value += 1
                j+= 1
                # print(value)
            if value <= 0:
                # print("vote error")
                return "error"


            honest = 0
            corrupt = 0
            tag = 0
            for j in range(i, MAX_SLOT):
                # print("---------------------------------------")
                # print(tag)
                sl = i+j
                if Beacon.select(sl) == Beacon.corrupt or sl%R == 0:
                    corrupt += 1
                else:
                    honest += 1
                if tag ==1:
                    if honest-corrupt>2*CP_K:
                        break
                    elif corrupt>= honest:
                        return "error"
                elif j-i>2*VOTELEN:
                    tag = 1
            
        return "right"
    def chain_judge(self):
        for i in range(0, MAX_SLOT-CP_K,1):
            honest = 0
            corrupt = 0
            tag = 0
            for j in range(i, MAX_SLOT):
                # print("---------------------------------------")
                # print(tag)
                sl = i+j
                if Beacon.select(sl) == Beacon.corrupt or sl%R == 0:
                    corrupt += 1
                else:
                    honest += 1
                if tag ==1:
                    if honest-corrupt>2*CP_K:
                        break
                    elif corrupt>= honest:
                        # print("honest:"+str(honest))
                        # print("corrupt:"+str(corrupt))      
                        # print("haha")
                        return "error"
                elif honest>CP_K or j-i>2*CP_K:
                    tag = 1
            # print("honest:"+str(honest))
            # print("corrupt:"+str(corrupt))
        return "right"
    def length(self, mylength = 0):
        if len(self.child) == 0:
            return 0
        length_list = []
        for node in self.child:
            length_tem = node.length() 
            length_list.append(length_tem)
        mylength += max(length_list)+1
        return mylength

def main():
    global USER_NUMBER,MAX_OUTPUTIP, MAX_INPUTIP, R, CP_K, MAX_SLOT, VOTELEN, EP, VOTELEN, VOTESPACE

    USER_NUMBER = parameters.USER_NUMBER
    MAX_OUTPUTIP = parameters.MAX_OUTPUTIP
    MAX_INPUTIP = parameters.MAX_INPUTIP
    R = parameters.EPOCH
    CP_K = parameters.CP_K
    MAX_SLOT = parameters.MAX_SLOT
    EP = parameters.EPISLON
    VOTELEN = 2*CP_K
    VOTESPACE = R
    Beacon.init_U(EP, parameters.SEED)
    # while len(Beacon.rand_list)<MAX_SLOT:
    #     Beacon.select(len(Beacon.rand_list)+1)
    # print(Beacon.u_list)
    # print("-------------------------------------------------------------------------")
    # print(CP_K)
    # print("-------------------------------------------------------------------------")
    tree = Tree()

    ans1 = tree.chain_judge()
    ans2 = tree.vote_judge()
    # print("-------------------------------------------------------------------------")
    # print(CP_K)
    # print("-------------------------------------------------------------------------")

    ans = {"chain_sec":ans1, "vote_sec":ans2}
    return ans


if __name__ == '__main__':
    main()