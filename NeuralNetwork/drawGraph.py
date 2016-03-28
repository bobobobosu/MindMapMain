import networkx as nx

import matplotlib.image as mpimg
try:
    import matplotlib.pyplot as plt
except:
    raise

class drawGraphClass:

    def drawGraph(self,inputList):
        print(inputList)
        self.G=nx.Graph()

        for connections in  inputList[1]:
            self.G.add_edge(connections[0],connections[1],weight=connections[2])
            print('conn')
            print(connections)

        for nodes in inputList[0]:
            try:
                self.G.add_node(image =mpimg.imread(nodes))
            except:
                self.G.add_node(nodes)
        self.elarge=[(u,v) for (u,v,d) in self.G.edges(data=True) if d['weight'] >0.5]
        self.esmall=[(u,v) for (u,v,d) in self.G.edges(data=True) if d['weight'] <=0.5]

        pos=nx.spring_layout(self.G,scale=0.02) # positions for all nodes

        '''
        # nodes
        nx.draw_networkx_nodes(self.G,pos,node_size=1400)

        # edges

        nx.draw_networkx_edges(self.G,pos,edgelist=self.elarge,
                        width=6)
        #nx.draw_networkx_edges(self.G,pos,edgelist=self.esmall,
        #                width=6,alpha=0.5,edge_color='b',style='dashed')

        # labels
        #nx.clustering(self.G)
        nx.draw_networkx_labels(self.G,pos,font_size=20,font_family='sans-serif')
'''
        nx.draw(self.G,with_labels=True)
        #nx.draw_random(self.G)
        #nx.draw_circular(self.G)
        #nx.draw_spectral(self.G,with_labels = True)


        plt.axis('off')
        plt.savefig("weighted_graph.png") # save as png
        plt.show() # display

