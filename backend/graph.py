class Graph(object):
    def __init__(self, layerDict):
        self.graph=layerDict
        self.copykeys=[]
        self.start_nodes=self.get_start_nodes(self.graph)
        self.end_points=self.get_end_points(self.graph)
        self.placeholders=self.start_nodes[:]

        self.graphs = self.create_graphs(self.graph, self.start_nodes, self.end_points)

    def get_start_nodes(self,graph):
        start_nodes=[]
        for Id, content in self.graph.items():
            if not content["backward_connections"]:
                start_nodes.append(Id)
        return start_nodes

    def get_end_points(self,graph):
        end_points=[]
        for Id, content in self.graph.items():
            if not content["forward_connections"]:
                end_points.append(Id)
        return end_points
    
    def create_graphs(self, graph, start, end_points):
        cyclicCheck={}
        visited, queue = {}, start[:]
        while queue:
            queueLen=len(queue)
            Id = queue.pop(0)
            # try:
            #     cyclicCheck[Id]+=1
            # except:
            #     cyclicCheck[Id]=0
            # if cyclicCheck[Id]>queueLen:
            #     raise Exception("Could not order the graph, maybe there is a cyclical connection?")
            #if graph[Id]["Type"]==("Train" or "Data"):
            # if type(graph[Id]["code"]) is not str:
            #     if graph[Id]["code"]["type"]=="Train&Data":
                #self.placeholders.append(Id)

            if not set(self.graph[Id]["backward_connections"]).issubset(list(visited.keys())):
                if not queue:
                    pass
                else:
                    queue.append(Id)
            elif Id not in visited:
                visited[Id]=dict(Con=self.graph[Id]["backward_connections"],Info=graph[Id],Copy=False)
                for for_con in graph[Id]["forward_connections"]:
                    if for_con not in queue:
                        queue.append(for_con)
                # queue.extend(graph[Id]["forward_connections"])

        if any([True for Id in end_points if visited[Id]['Info']['Type']=='TrainReinforce']):
            visited=self.manipulate_graph(visited,start,end_points)
        return visited

    def manipulate_graph(self,graph,start_points,end_points):
        newGraph={}
        maxId=max([int(key) for key in graph.keys()])
        for endId in end_points:
            newGraph[endId]=graph[endId]
            if graph[endId]['Info']['Type']=='TrainReinforce':
                self.placeholders.append(endId)
                if graph[endId]['Info']['Properties']['ReinforceType']=='Q_learning':
                    for Id in graph:
                        newGraph[Id]=graph[Id]
                        if Id not in start_points and Id not in end_points:
                            if graph[Id]['Info']['backward_connections'][0] in start_points:
                                data_id=graph[Id]['Info']['backward_connections']
                                newGraph[str(maxId+int(Id))]=dict(Con=data_id,Info=graph[Id]['Info'],Copy=True,CopyOf=Id)
                                self.copykeys.append(str(maxId+int(Id)))
                                #newGraph[str(maxId+int(Id))]=dict(Con=[],Info=graph[Id]['Info'],Copy=True)
                            elif graph[Id]['Info']['forward_connections'][0] in end_points:
                                newGraph[str(maxId+int(Id))]=dict(Con=[str(int(con)+maxId) for con in graph[Id]['Info']["backward_connections"]],Info=graph[Id]['Info'],Copy=True,CopyOf=Id,Input_ref=data_id)
                                newGraph[endId]['Con'].append(str(maxId+int(Id)))
                                self.copykeys.append(str(maxId+int(Id)))
                            else:
                                newGraph[str(maxId+int(Id))]=dict(Con=[str(int(con)+maxId) for con in graph[Id]['Info']["backward_connections"]],Info=graph[Id]['Info'],CopyOf=Id,Copy=True)
                                self.copykeys.append(str(maxId+int(Id)))
                    newGraph.pop(endId)
                    newGraph[endId]=graph[endId]

                    layer_pairs = []
                    for id_ in newGraph:
                        copied_id = newGraph[id_].get('CopyOf')
                        if copied_id is None:
                            continue                        
                        layer_pairs.append((copied_id, id_))

                        if copied_id in newGraph[endId]['Con']:
                            online_net = copied_id
                            target_net = id_
                            newGraph[endId]['Con'].append(id_) # TODO: is backwards connections needed too?
                    
                    newGraph[endId]['Info']['ExtraInfo'] = dict()
                    newGraph[endId]['Info']['ExtraInfo']['Pairs'] = layer_pairs
                    newGraph[endId]['Info']['ExtraInfo']['OnlineNet'] = online_net
                    newGraph[endId]['Info']['ExtraInfo']['TargetNet'] = target_net                    
                elif graph[Id]['Info']['Properties']['ReinforceType']=='Policy_gradient':
                    pass
                elif graph[Id]['Info']['Properties']['ReinforceType']=='A2C':
                    pass
                elif graph[Id]['Info']['Properties']['ReinforceType']=='A3C':
                    pass
                elif graph[Id]['Info']['Properties']['ReinforceType']=='PPO':
                    pass
        return newGraph

if __name__ == "__main__":
    properties={
            "Name": "Data_1",
            "Type": "DataData",
            "Properties": {
                "Type": "Data",
                "accessProperties": {
                    "Columns": [],
                    "Dataset_size": 1,
                    "Category": "Local",
                    "Type": "Data",
                    "Partition_List":[[70,20,10],[60,30,10]],
                    "Path": [
                        "C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Data/mnist_split/mnist_input.npy",
                        "C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Data/mnist_split/mnist_input.npy"
                    ],
                    "Content": "",
                    "Warning": "Could not find path"
                }
            },
            "checkpoint": [],
            "endPoints": [],
            "backward_connections": [],
            "forward_connections": []
        }
    miniNet={"123":properties}
    graph=Graph(miniNet).graphs
    print(graph)
