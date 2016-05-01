"""A collection of different types of attacks on networks"""
import random

def random_attack(network, attack_length):
    """
    Given a network, attack that network for attack_length timesteps. This
    attack works by randomly removing nodes from the network. Returns the
    network after it has been attacked.
    """

    aftermath = network.copy()
    for _ in range(attack_length):
        node = random.choice(aftermath.nodes())
        aftermath.remove_node(node)

    print "Random attack on %d nodes complete" % (attack_length,)
    return aftermath

def targeted_attack(network, attack_length):
    """
    Given a network, attack that for snetwork attack_length timesteps
    by removing the node with the highest degree at each stepfrom the network.
    Returns the network after it has been attacked.
    """

    aftermath = network.copy()
    degs = {n : aftermath.degree(n) for n in aftermath.nodes()}

    for _ in range(attack_length):
        node = max(degs, key=degs.get)
        for neighbor in aftermath.neighbors(node):
            degs[neighbor] -= 1
        aftermath.remove_node(node)
        del degs[node]

    print "Targeted attack on %d nodes complete" % (attack_length,)
    return aftermath

def targeted_neighbor_attack(network, attack_length):
    """
    Given a network, attack that network for attack_length timesteps. This
    attack works by randomly selecting a starting node, removing it, and then
    proceeding to the neighbor of the original node with the highest degree
    to repeat the process. Returns the network after the attack.
    """
    aftermath = network.copy()

    degs = {n : aftermath.degree(n) for n in aftermath.nodes()}

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
        for neighbor in aftermath.neighbors(node):
            degs[neighbor] -= 1

        aftermath.remove_node(node)
        del degs[node]
        node = next_node
    print "Targeted-neighbor attack on %d nodes complete" % \
          (attack_length,)
    return aftermath

def random_neighbor_attack(network, attack_length):
    """
    Given a network, attack that network for attack_length timesteps. This
    attack works by randomly selecting a starting node, removing it, and then
    proceeding to a random neighbor of the original node to repeat the process.
    Returns the network after the attack.
    """
    aftermath = network.copy()

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
    print "Random-neighbor attack on %d nodes complete" % \
          (attack_length,)
    return aftermath
