"""A collection of functions to run attacks and evaluate network breakdown."""

from multiprocessing import Pipe, Process
from multiprocessing.pool import ThreadPool
import networkx
from attack_tools import (random_attack, targeted_attack, random_neighbor_attack,
                          targeted_neighbor_attack)
                          
def gc_size(network, N):
    """Calculate the proportion of nodes in the largest component of
    the network"""
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
    """
    Given an attack function to run, and a Connection object through which to
    communicate, receive a network and set of fractions of the total nodes to
    remove, and simulate attacks on that network for each fraction in an
    iterative manner by attacking the end result of each the previous attack.
    Sends S1/N back through the Connection for each fraction.
    """
    network = pipe.recv()
    fractions = pipe.recv()

    N = len(network)
    nodes_to_remove = [f*N for f in fractions]
    node_remove_deltas = [int(nodes_to_remove[0])] + \
                         [int(round(nodes_to_remove[i] - nodes_to_remove[i-1]))
                          for i in range(1, len(nodes_to_remove))]
    for num_nodes in node_remove_deltas:
        network = attack(network, num_nodes)
        pipe.send(gc_size(network, N))
    pipe.close()

def attack_comparison_async(network, fractions):
    """
    Given a network to attack, a list of fractions of nodes to remove from the
    network, and a list of attack functions, run those attack functions on the
    network over the given node fractions asynchronously and return the results
    of each attack function.
    """


    random_parent, random_child = Pipe()
    targeted_parent, targeted_child = Pipe()
    rn_parent, rn_child = Pipe()
    tn_parent, tn_child = Pipe()

    rnd = Process(name="random", target=run_sweeping_attack,
                  args=(random_attack, random_child,))
    tgt = Process(name="targeted", target=run_sweeping_attack,
                  args=(targeted_attack, targeted_child,))
    rnd_neighbor = Process(name="random_neighbor", target=run_sweeping_attack,
                           args=(random_neighbor_attack, rn_child,))
    tgt_neighbor = Process(name="Targeted_neighbor", target=run_sweeping_attack,
                           args=(targeted_neighbor_attack, tn_child,))



    rnd.start()
    tgt.start()
    rnd_neighbor.start()
    tgt_neighbor.start()

    for pipe in [random_parent, targeted_parent, rn_parent, tn_parent]:
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

    while random_parent.poll():
        random_results.append(random_parent.recv())
    random_parent.close()
    print len(random_results), "random results recieved"

    while targeted_parent.poll():
        targeted_results.append(targeted_parent.recv())
    targeted_parent.close()
    print len(targeted_results), "targeted results recieved"

    while rn_parent.poll():
        rn_results.append(rn_parent.recv())
    rn_parent.close()
    print len(rn_results), "random neighbor results recieved"

    while tn_parent.poll():
        tn_results.append(tn_parent.recv())
    tn_parent.close()
    print len(tn_results), "targeted neighbor results recieved"

    print "Attack Comparison Complete"
    return random_results, targeted_results, rn_results, tn_results
