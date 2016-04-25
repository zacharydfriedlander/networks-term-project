import networkx, random
from multiprocessing import Process, Queue
from multiprocessing.pool import ThreadPool
import time

def random_attack(network, attack_length):
    """
    Given a network, 'attack' that network by randomly removing
    attack_length nodes from the network. Returns the new network
    after it has been attacked.
    """

    aftermath = network.copy()
    tstart = time.clock()
    for _ in range(attack_length):
        u = random.choice(aftermath.nodes())
        aftermath.remove_node(u)

    print "Random attack on %d nodes complete (%f seconds)" % (attack_length,
                                                               time.clock() - tstart)
    return aftermath

def targeted_attack(network, attack_length):
    """
    Given a network, 'attack' that network attack_length times
    by removing the highest-degree node from the network.
    Returns the new network after it has been attacked.
    """

    aftermath = network.copy()
    degs = {n : aftermath.degree(n) for n in aftermath.nodes()}

    tstart = time.clock()

    for _ in range(attack_length):
        u = max(degs, key=degs.get)
        for node in aftermath.neighbors(u):
            degs[node] -= 1
        aftermath.remove_node(u)
        del degs[u]

    print "Targeted attack on %d nodes complete (%f seconds)" % (attack_length,
                                                               time.clock() - tstart)
    return aftermath

def random_neighbor_attack(network, attack_length):
    aftermath = network.copy()

    degs = {n : aftermath.degree(n) for n in aftermath.nodes()}

    tstart = time.clock()

    node = random.choice(aftermath.nodes())

    for _ in range(attack_length):
        if aftermath.degree(node) == 0 or aftermath.neighbors(node) == [node]:

            other_nodes = [n for n in aftermath.nodes() if n != node]
            next_node = random.choice(other_nodes)
        else:
            while True:
                neighbor_degs = {n : degs[n] for n in aftermath.neighbors(node)
                                 if n != node}
                next_node = max(neighbor_degs, key=neighbor_degs.get)
                if next_node != node:
                    break
        for n in aftermath.neighbors(node):
            degs[n] -= 1

        aftermath.remove_node(node)
        del degs[node]
        node = next_node
    print "Targetd-neighbor attack on %d nodes complete (%f seconds)" % \
          (attack_length, time.clock() - tstart)
    return aftermath

def targeted_neighbor_attack(network, attack_length):
    aftermath = network.copy()

    tstart = time.clock()

    node = random.choice(aftermath.nodes())

    for _ in range(attack_length):
        if aftermath.degree(node) == 0 or aftermath.neighbors(node) == [node]:
            other_nodes = [n for n in aftermath.nodes() if n != node]
            next_node = random.choice(other_nodes)
        else:
            while True:
                next_node = random.choice(aftermath.neighbors(node))
                if next_node != node:
                    break
        aftermath.remove_node(node)
        node = next_node
    print "Targeted-neighbor attack on %d nodes complete (%f seconds)" % \
          (attack_length, time.clock() - tstart)
    return aftermath

def gc_size(network, N):
        return len(max(networkx.connected_components(network),
               key=len)) / float(N)

def run_attack(network, fractions, attack, result_q):
    """
    Given a network and set of node fractions to remove,
    as well as an attack function to run, simulate attacks
    on that network and put s1/N for each attack in the result queue
    """
    N = len(network)
    nodes_to_remove = [int(round(f * N)) for f in fractions]


    thread_pool = ThreadPool(len(fractions))
    results = thread_pool.imap(lambda x: attack(network, x), nodes_to_remove)

    i = 0
    for res in results:
        i += 1
        result_q.put(gc_size(res, N))

def attack_comparison_async(network, fractions):

    random_q = Queue()
    targeted_q = Queue()
    rn_q = Queue()
    tn_q = Queue()
    N = len(network)


    rnd = Process(target=run_attack, args=(network, fractions, random_attack,
                                           random_q,))
    tgt = Process(target=run_attack, args=(network, fractions, targeted_attack,
                                           targeted_q,))
    rnd_neighbor = Process(target=run_attack, args=(network, fractions,
                                           random_neighbor_attack, rn_q))
    tgt_neighbor = Process(target=run_attack, args=(network, fractions,
                                           targeted_neighbor_attack, tn_q))


    rnd.start()
    tgt.start()
    rnd_neighbor.start()
    tgt_neighbor.start()

    rnd.join()
    tgt.join()
    rnd_neighbor.join()
    tgt_neighbor.join()

    random_results = []
    targeted_results = []
    rn_results = []
    tn_results = []

    while not(random_q.empty()):
        random_results.append(random_q.get())
    while not(targeted_q.empty()):
        targeted_results.append(targeted_q.get())
    while not(rn_q.empty()):
        rn_results.append(rn_q.get())
    while not(tn_q.empty()):
        tn_results.append(tn_q.get())


    print "Attack Comparison Complete"
    return random_results, targeted_results, rn_results, tn_results
