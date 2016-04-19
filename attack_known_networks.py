#! /usr/bin/env python2

import networkx
import attack_comparison as ac
from numpy import linspace
import yaml
import os.path
import argparse

def main():

    aparse = argparse.ArgumentParser(usage="Attack a collection of networks")
    aparse.add_argument('--network_file', '-f', action='store',
                        default='networks.yaml',
                        help="Path to network config (default: ./networks.yaml)",
                        dest='config_path'
                        )
    aparse.add_argument('--picklejar', '-p', action='store',
                        default='.',
                        help='output for pickle files (default: current directory)',
                        )
    args = aparse.parse_args()

    cfg = open(args.config_path, 'r')

    FRACS = linspace(0.05, 0.95, 19)

    for net_attrs in yaml.safe_load_all(cfg):

        print "Analyzing network %s..." % net_attrs['name']
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
        pckl = os.path.normpath(args.picklejar+"/"+net_attrs['name']+
                                ".pickle")

        ac.compare_to_random_networks(network, FRACS, pckl)

        print "Done!"

if __name__ == "__main__":
    main()
