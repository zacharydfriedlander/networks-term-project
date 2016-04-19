import networkx
from attack_tools import attack_comparison_async
import pickle

def compare_to_random_networks(network, fractions, pfile):
    """
    Given a network, a list of fractions over which to operate, and
    a name to use for the pickle file, run the targeted and random attacks over
    the network, as well as its Erdos-Renyi and Configuration model
    counterparts. Pickles all data into the given pickle filename
    """
    print "Attacking network..."
    rnd, tgt = attack_comparison_async(network, fractions)

    # Create an Erdos-Renyi graph with the same number of nodes and edges
    N = network.number_of_nodes()
    M = network.number_of_edges()
    er = networkx.generators.gnm_random_graph(N, M)

    print "Attacking ER network..."
    er_rnd, er_tgt = attack_comparison_async(er,fractions)

    # Create a configuration-model graph with the same degree sequence
    config = networkx.generators.configuration_model(network.degree().values(),
                                                  create_using=networkx.Graph())
    print "Attacking Config network..."
    cfg_rnd, cfg_tgt = attack_comparison_async(config, fractions)

    # Pickle all information

    pickle_f = open(pfile, 'w')

    pickle.dump(fractions, pickle_f)
    pickle.dump((rnd, tgt), pickle_f)
    pickle.dump((er_rnd, er_tgt), pickle_f)
    pickle.dump((cfg_rnd, cfg_tgt), pickle_f)

    pickle_f.close()
