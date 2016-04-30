from multiprocessing import Pipe, Process
from multiprocessing.pool import ThreadPool
import networkx
from attack_tools import *

def gc_size(network, N):
        return len(max(networkx.connected_components(network),
               key=len)) / float(N)

def run_attack(attack, pipe):
    """
    Given an attack function to run, and a Connection object through which to
    communicate, receive a network and set of fractions to remove, and simulate
    attacks on that network for each fraction of nodes. Puts S1/N back through
    the pipe for each fraction.
    """
    network = pipe.recv()
    fractions = pipe.recv()

    N = len(network)
    nodes_to_remove = [int(round(f * N)) for f in fractions]

    thread_pool = ThreadPool(5)
    results = thread_pool.imap(lambda x: attack(network, x), nodes_to_remove)

    for res in results:
        pipe.send(gc_size(res, N))
    pipe.close()

def run_sweeping_attack(attack, pipe):
    network = pipe.recv()
    fractions = pipe.recv()

    N = len(network)
    nodes_to_remove = [f*N for f in fractions]
    node_remove_deltas = [int(nodes_to_remove[0])] + [int(round(nodes_to_remove[i]
                                                 - nodes_to_remove[i-1])) for i in
                                                 range(1,len(nodes_to_remove))]
    for num_nodes in node_remove_deltas:
        network = attack(network, num_nodes)
        pipe.send(gc_size(network, N))
    pipe.close()

def attack_comparison_async(network, fractions):

    r1, r2 = Pipe()
    t1, t2 = Pipe()
    rn1, rn2 = Pipe()
    tn1, tn2 = Pipe()
    N = len(network)


    rnd = Process(name="random", target=run_sweeping_attack,
                  args=(random_attack, r2,))
    tgt = Process(name="targeted", target=run_sweeping_attack,
                  args=(targeted_attack, t2,))
    rnd_neighbor = Process(name="random_neighbor", target=run_sweeping_attack,
                           args=(random_neighbor_attack, rn2,))
    tgt_neighbor = Process(name="Targeted_neighbor", target=run_sweeping_attack,
                           args=(targeted_neighbor_attack, tn2,))



    rnd.start()
    tgt.start()
    rnd_neighbor.start()
    tgt_neighbor.start()

    for pipe in [r1, t1, rn1, tn1]:
        pipe.send(network)
        pipe.send(fractions)

    rnd.join()
    tgt.join()
    rnd_neighbor.join()
    tgt_neighbor.join()

    random_results = []
    targeted_results = []
    rn_results = []
    tn_results = []

    while r1.poll():
        random_results.append(r1.recv())
    r1.close()
    print len(random_results), "random results recieved"

    while t1.poll():
        targeted_results.append(t1.recv())
    t1.close()
    print len(targeted_results), "targeted results recieved"

    while rn1.poll():
        rn_results.append(rn1.recv())
    rn1.close()
    print len(rn_results), "random neighbor results recieved"

    while tn1.poll():
        tn_results.append(tn1.recv())
    tn1.close()
    print len(tn_results), "targeted neighbor results recieved"

    print "Attack Comparison Complete"
    return random_results, targeted_results, rn_results, tn_results
