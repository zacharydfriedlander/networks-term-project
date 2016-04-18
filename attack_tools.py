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

    print "RANDOM: removed %d nodes in %f s" % (attack_length, time.clock() -
                                                tstart)

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

    print "TARGETED: removed %d nodes in %f s" % (attack_length, time.clock()
                                                  - tstart)


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
    N = len(network)
    rnd = Process(target=run_attack, args=(network, fractions, random_attack,
                                           random_q,))
    tgt = Process(target=run_attack, args=(network, fractions, targeted_attack,
                                           targeted_q,))

    rnd.start()
    tgt.start()

    rnd.join()
    tgt.join()

    random_results, targeted_results = [], []

    while not(random_q.empty()):
        random_results.append(random_q.get())
    while not(targeted_q.empty()):
        targeted_results.append(targeted_q.get())

    return random_results, targeted_results

def attack_comparison_sync(network, fractions):
    """
    Given a network and set of node fractions to remove,
    simulate random and targeted attacks on that network
    and return s1/N for the results of each attack. Used as
    A sanity check for attack_comparisons_async
    """

    N = len(network)
    nodes_to_remove = [int(round(f * N)) for f in fractions]

    random_largest_component, targeted_largest_component = [], []

    for n in nodes_to_remove:
        random_result = random_attack(network, n)
        targeted_result = targeted_attack(network, n)
        random_largest_component.append(gc_size(random_result, N))
        targeted_largest_component.append(gc_size(targeted_result, N))

    return random_largest_component, targeted_largest_component
