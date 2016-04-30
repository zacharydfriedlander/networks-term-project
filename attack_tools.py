import random, time

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

    print "Random attack on %d nodes complete" % (attack_length,)
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

    print "Targeted attack on %d nodes complete" % (attack_length,)
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
    print "Random-neighbor attack on %d nodes complete" % \
          (attack_length,)
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
    print "Targeted-neighbor attack on %d nodes complete" % \
          (attack_length,)
    return aftermath
