#! /usr/bin/env python2

import networkx
import attack_comparison as ac
from numpy import linspace
import yaml
import sys
import argparse

def main():

    aparse = argparse.ArgumentParser(usage="Attack a collection of networks")
    aparse.add_argument('--network_file', '-f',
                        action='store',
                        default='networks.yaml',
                        help="Path to network config (default: ./networks.yaml)",
                        dest='config_path'
                        )
    args = aparse.parse_args()

    cfg = open(args.config_path, 'r')
    # orgnet = networkx.read_edgelist("datasets/org_net_informal_links.txt",
    #                   create_using=networkx.Graph(),
    #                   nodetype=str,
    #                   data = [('weight', float)])

    # yeast = networkx.read_edgelist("datasets/Yeast_transcription.txt",
    #                   create_using=networkx.Graph(),
    #                   nodetype=str,
    #                   data = [('weight', float)])


    # wag = networkx.read_edgelist("datasets/word_association_graph_DSF.txt",
    #                   create_using=networkx.DiGraph(),
    #                   nodetype=str,
    #                   data = [('weight', float)]).to_undirected()


    # ORGNET_PCKL = "picklejar/orgnet.pickle"
    # YEAST_PCKL = "picklejar/yeast.pickle"
    # WAG_PCKL = "picklejar/wag.pickle"
    FRACS = linspace(0.05, 0.95, 19)

    for net_attrs in yaml.safe_load_all(cfg):

        print "----------------------BEGIN NETWORK %s ----------------------" % net_attrs['name']
        fname = net_attrs['filename']
        data = [(key, eval(value)) for key, value in net_attrs['data'].items()]
        if net_attrs["directed"]:
            network = networkx.read_edgelist(fname,
                                             create_using=networkx.DiGraph(),
                                             nodetype=str,
                                             data=data).to_undirected()
        else:
            network = networkx.read_edgelist(fname,
                                             create_using=networkx.Graph(),
                                             nodetype=str,
                                             data=data)
        pckl = net_attrs['name']+".pickle"

        ac.compare_to_random_networks(network, FRACS, pckl)

    #ac.compare_to_random_networks(orgnet, FRACS, ORGNET_PCKL)
    #print "----------------------BEGIN YEAST----------------------"
    #ac.compare_to_random_networks(yeast, FRACS, YEAST_PCKL)
    #print "----------------------BEGIN WAG----------------------"
    #ac.compare_to_random_networks(wag, FRACS, WAG_PCKL)
    #print "----------------------ATTACKS COMPLETE----------------------"

if __name__ == "__main__":
    main()
