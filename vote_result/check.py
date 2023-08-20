SE_PATH = "./se_result"
NS_PATH = "./ns_result"
import matplotlib.pyplot   as plt
import json
font_size = 15
from matplotlib import rcParams

# import matplotlib
plt.rcParams["mathtext.fontset"] = "cm"

def plot_by_ep(k, msg):
    msg1 = json.loads(msg)
    ans_list = []
    for ele in msg1:
        if ele["CP_k"] == k:
            ans_list.append(ele)
    x = []
    y_chain = []
    y_vote = []
    for ele in ans_list:
        x.append(ele["EP"])
        y_chain.append(1-ele["chain_acc"])
        y_vote.append(1-ele["vote_acc"])
    return (x, y_chain, y_vote)
def plot_by_k(ep, msg):
    msg1 = json.loads(msg)
    ans_list = []
    for ele in msg1:
        if ele["EP"] == ep:
            ans_list.append(ele)
    x = []
    y_chain = []
    y_vote = []
    for ele in ans_list:
        x.append(ele["CP_k"])
        y_chain.append(1-ele["chain_acc"])
        y_vote.append(1-ele["vote_acc"])
    return (x, y_chain, y_vote)

def plot_by_n( msg):
    msg1 = json.loads(msg)
    ans_list = []
    ep = msg1[0]["EP"]
    k = msg1[0]["CP_k"]
    for ele in msg1:
        if ele["EP"] == ep and ele["CP_k"] == k:
            ans_list.append(ele)
    x = []
    y_chain = []
    y_vote = []
    for ele in ans_list:
        x.append(ele["MAX_SLOT"])
        y_chain.append(1-ele["chain_acc"])
        y_vote.append(1-ele["vote_acc"])
    return (x, y_chain, y_vote)

def plot_EP(plt):
    with open(SE_PATH, "r") as f:
        msg1 = f.read()
    with open(NS_PATH, "r") as f:
        msg2 = f.read()
    k = 13
    [x, y_se_chain, y_se_vote] = plot_by_ep(k,msg1)
    [x, y_ne_chain, y_ne_vote] = plot_by_ep(k,msg2)
    print(x)
    plt.plot(x,y_se_chain,".--",color="orange")
    plt.plot(x,y_se_vote,color="orange")
    plt.plot(x,y_ne_chain,".--",color="green")
    plt.plot(x,y_ne_vote,color="green")
    # plt.text(-0.04, 0.5, 'C', va='center', fontsize=15)
    
    plt.set_xlabel("$\epsilon$" , fontsize=18)
    plt.xaxis.set_label_coords(1.03, 0.01)

    return plt
def plot_SEP(plt):
    with open("./data ep=0.08/se_result", "r") as f:
        msg1 = f.read()
    with open("./data ep=0.08/ns_result", "r") as f:
        msg2 = f.read()

    ep = 0.08
    [x, y_se_chain, y_se_vote] = plot_by_k(ep,msg1)
    [x, y_ne_chain, y_ne_vote] = plot_by_k(ep,msg2)

    plt.plot(x,y_se_chain,".--",color="orange")
    plt.plot(x,y_se_vote,color="orange")
    plt.plot(x,y_ne_chain,".--",color="green")
    plt.plot(x,y_ne_vote,color="green")
    plt.set_xlabel("$k$", fontsize=18)
    plt.xaxis.set_label_coords(1.03, 0.01)
    # plt.text(-0.04, 0.5, 'B', va='center', fontsize=15)
    return plt
def plot_k(plt):
    with open("./finaldata/se_result", "r") as f:
        msg1 = f.read()
    with open("./finaldata/ns_result", "r") as f:
        msg2 = f.read()

    ep = 0.3
    [x, y_se_chain, y_se_vote] = plot_by_k(ep,msg1)
    [x, y_ne_chain, y_ne_vote] = plot_by_k(ep,msg2)

    plt.plot(x,y_se_chain,".--",color="orange")
    plt.plot(x,y_se_vote,color="orange")
    plt.plot(x,y_ne_chain,".--",color="green")
    plt.plot(x,y_ne_vote,color="green")
    plt.set_xlabel("$k$", fontsize=18)
    plt.xaxis.set_label_coords(1.03, 0.01)
    # plt.text(-0.04, 0.5, 'A', va='center', fontsize=15)
    return plt

def plot_n(plt):
    with open("./finaldata3/se_result", "r") as f:
        msg1 = f.read()
    with open("./finaldata3/ns_result", "r") as f:
        msg2 = f.read()

    # ep = 0.3
    [x, y_se_chain, y_se_vote] = plot_by_n(msg1)
    [x, y_ne_chain, y_ne_vote] = plot_by_n(msg2)

    plt.plot(x,y_se_chain,".--",color="orange", label=r'$ \mathbf{\epsilon_{Chain}}(VF)$')
    plt.plot(x,y_se_vote,color="orange",label=r'$ \mathbf{\epsilon_{Vote}}(VF)$')
    plt.plot(x,y_ne_chain,".--",color="green",label=r'$ \mathbf{\epsilon_{Chain}}(CBV)$')
    plt.plot(x,y_ne_vote,color="green",label=r'$\mathbf{\epsilon_{Vote}}(CBV)$')
    plt.set_xlabel("$n$", fontsize=18)
    plt.xaxis.set_label_coords(1.03, 0.01)
    # plt.text(-0.04, 0.5, 'D', va='center', fontsize=15)
    return plt


def main():
    fig  = plt.figure()
    ax1 = fig.add_subplot(4, 1, 1)
    ax2 = fig.add_subplot(4, 1, 2,sharey=ax1)
    ax3 = fig.add_subplot(4, 1, 3,sharey=ax1)
    ax4 = fig.add_subplot(4, 1, 4,sharey=ax1)
    handles, labels = ax4.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center')
    plot_k(ax1)
    plot_SEP(ax2)
    plot_EP(ax3)
    plot_n(ax4)
    # ax1.tick_params(axis='both', which='major', labelsize=15)
    # ax2.tick_params(axis='both', which='minor', labelsize=6)
    # plt.tick_params(labelsize=21)
    fig.legend(fontsize=font_size, loc="lower center", ncol = 4)
    # plt.tight_layout()
    # fig.text(0.5, 0.04, 'common X', ha='center')
    fig.text(0.05, 0.5, 'Probability of Property Violations', va='center', rotation='vertical', fontsize=17)
    fig.text(0.08, 0.2, 'D', va='center', fontsize=15)
    fig.text(0.08, 0.43, 'C', va='center', fontsize=15)
    fig.text(0.08, 0.66, 'B', va='center', fontsize=15)
    fig.text(0.08, 0.9, 'A', va='center', fontsize=15)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=0.98, wspace=0.1, hspace=0.4)
    # fig.title("The ")
    plt.show()

    plt.savefig("./ficture", dpi=100000, format="svg")
     


if __name__ == "__main__":
    main()