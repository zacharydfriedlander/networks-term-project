#! /usr/bin/env python2

import networkx
import attack_comparison as ac
from numpy import linspace
def main():
    orgnet = networkx.read_edgelist("datasets/org_net_informal_links.txt",
                      create_using=networkx.Graph(),
                      nodetype=str,
                      data = [('weight', float)])

    yeast = networkx.read_edgelist("datasets/Yeast_transcription.txt",
                      create_using=networkx.Graph(),
                      nodetype=str,
                      data = [('weight', float)])


    wag = networkx.read_edgelist("datasets/word_association_graph_DSF.txt",
                      create_using=networkx.DiGraph(),
                      nodetype=str,
                      data = [('weight', float)]).to_undirected()
    FRACS = linspace(0.05, 0.95, 19)

    ORGNET_PCKL = "picklejar/orgnet.pickle"
    YEAST_PCKL = "picklejar/yeast.pickle"
    WAG_PCKL = "picklejar/wag.pickle"

    print "----------------------BEGIN ORGNET----------------------"
    ac.compare_to_random_networks(orgnet, FRACS, ORGNET_PCKL)
    print "----------------------BEGIN YEAST----------------------"
    ac.compare_to_random_networks(yeast, FRACS, YEAST_PCKL)
    print "----------------------BEGIN WAG----------------------"
    ac.compare_to_random_networks(wag, FRACS, WAG_PCKL)
    print "----------------------ATTACKS COMPLETE----------------------"

if __name__ == "__main__":
    main()
