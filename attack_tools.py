import networkx, random
from multiprocessing import Process, Pipe, current_process
from multiprocessing.pool import ThreadPool
import time

def random_attack(network, attack_length):
    """
    Given a network, 'attack' that network by randomly removing
    attack_length nodes from the network. Returns the new network
    after it has been attacked.
    """
    print "RANDOM"
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
    print "TARGETED"
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
    print "Random-neighbor attack on %d nodes complete (%f seconds)" % \
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

def run_attack(attack, pipe):
    """
    Given an attack function to run, and a Connection object through which to
    communicate, receive a network and set of fractions to remove, and simulate
    attacks on that network for each fraction of nodes. Puts S1/N back through
    the pipe for each fraction.
    """
    print current_process().name, "running attacks"
    network = pipe.recv()
    fractions = pipe.recv()

    N = len(network)
    nodes_to_remove = [int(round(f * N)) for f in fractions]

    print current_process().name, "Starting map..."
    thread_pool = ThreadPool(5)
    results = thread_pool.imap(lambda x: attack(network, x), nodes_to_remove)

    i = 0
    for res in results:
        i += 1
        pipe.send(gc_size(res, N))
    pipe.close()

def attack_comparison_async(network, fractions):

    r1, r2 = Pipe()
    t1, t2 = Pipe()
    rn1, rn2 = Pipe()
    tn1, tn2 = Pipe()
    N = len(network)


    rnd = Process(name="random", target=run_attack, args=(random_attack,
                                           r2,))
    tgt = Process(name="targeted", target=run_attack, args=(targeted_attack,
                                           t2,))
    rnd_neighbor = Process(name="random_neighbor", target=run_attack,
                           args=(random_neighbor_attack, rn2,))
    tgt_neighbor = Process(name="Targeted_neighbor", target=run_attack,
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
    print "All Processes joined. Reaping results..."
    random_results = []
    targeted_results = []
    rn_results = []
    tn_results = []

    while r1.poll():
        random_results.append(r1.recv())
    r1.close()

    while t1.poll():
        targeted_results.append(t1.recv())
    t1.close()

    while rn1.poll():
        rn_results.append(rn1.recv())
    rn1.close()

    while tn1.poll():
        tn_results.append(tn1.recv())
    tn1.close()

    print "Attack Comparison Complete"
    return random_results, targeted_results, rn_results, tn_results
