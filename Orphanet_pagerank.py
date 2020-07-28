import networkx as nx
import csv

orpha_graph = nx.read_gexf("orphanet-hpo.gexf")
o_weights = nx.pagerank_numpy(orpha_graph)

with open('orphanet_weights.csv', 'w') as f:
    for key in o_weights.keys():
        f.write("%s,%s\n"%(key,o_weights[key]))
