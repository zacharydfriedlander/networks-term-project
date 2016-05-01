#! /usr/bin/env python2
""" Main Module"""
import argparse
import os.path

import yaml
import networkx

from numpy import linspace
import attack_comparison as ac

FRACS = linspace(0.05, 0.95, 19)

def main():
    """
    Program Driver. Parses command line arguments to determine where to store
    output pickle files and what networks to attack, reads in networks from the
    given source, runs all necessary attacks, and pickles the output for later
    use.
    """

    aparse = argparse.ArgumentParser(usage="Attack a collection of networks")
    aparse.add_argument('--network_file', '-f', action='store',
                        default='networks.yaml',
                        help="Path to network config (default: ./networks.yaml)",
                        dest='config_path')
    aparse.add_argument('--picklejar', '-p', action='store',
                        default='.',
                        help='output for pickle files (default: current directory)',
                       )
    aparse.add_argument('--update', '-u', action='store_true',
                        help='Only run network processes for networks which have' +
                        'not already been analyzed.')
    args = aparse.parse_args()

    cfg = open(args.config_path, 'r')


    for net_attrs in yaml.safe_load_all(cfg):
        picklename = net_attrs["name"] + ".pickle"
        if args.update and picklename in os.listdir(args.picklejar):
            continue

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
        print "Network file loaded"
        pckl = os.path.normpath(args.picklejar+"/"+ picklename)
        ac.compare_to_random_networks(network, FRACS, pckl)

        print "Done!"

if __name__ == "__main__":
    main()
