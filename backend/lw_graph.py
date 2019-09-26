class Graph(object):
    def __init__(self, layerDict):
        self.graph=layerDict
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
        visited, queue = {}, start[:]
        while queue:
            Id = queue.pop(0)
            if not set(self.graph[Id]["backward_connections"]).issubset(list(visited.keys())):
                # print(list(visited.keys()))
                # print(list(set(self.graph[Id]["backward_connections"])))
                # print(list(set(self.graph[Id]["backward_connections"])-set(list(visited.keys()))))
                if not queue:
                    # pass
                    queue.extend(list(set(self.graph[Id]["backward_connections"])-set(list(visited.keys()))))
                    visited[Id]=dict(Con=self.graph[Id]["backward_connections"],Info=graph[Id],Copy=False)
                else:
                    queue.append(Id)
            elif Id not in visited:
                visited[Id]=dict(Con=self.graph[Id]["backward_connections"],Info=graph[Id],Copy=False)
                queue.extend(graph[Id]["forward_connections"])

        return visited

# layers={
#     "1":{
#         "backward_connections": [],
#         "forward_connections": ["2"]
#     },
#     "2":{
#         "backward_connections": ["1","4"],
#         "forward_connections": ["3"]
#     },
#     "3":{
#         "backward_connections": ["2"],
#         "forward_connections": ["4"]
#     },
#     "4":{
#         "backward_connections": ["3"],
#         "forward_connections": ["2"]
#     },
# }
# layers={
#     "2": {
#         "backward_connections": [],
#         "forward_connections": ["3"]
#     },
#     "3": {
#         "backward_connections": ["2"],
#         "forward_connections": ["4"]
#     },
#     "4": {
#         "backward_connections": [
#         "3"
#         ],
#         "forward_connections": [
#         "5"
#         ]
#     },
#     "5": {
#         "backward_connections": [
#         "4"
#         ],
#         "forward_connections": [
#         "10"
#         ]
#     },
#     "10": {
#         "backward_connections": [
#         "5",
#         "11"
#         ],
#         "forward_connections": []
#     },
#     "11": {
#         "backward_connections": [
#         "12"
#         ],
#         "forward_connections": [
#         "10"
#         ]
#     },
#     "12": {
#         "backward_connections": [],
#         "forward_connections": [
#         "11"
#         ]
#     },
#     "13":{
#         "backward_connections": [],
#         "forward_connections": [
#         "14"
#         ]
#     },
#     "14":{
#         "backward_connections": ["13"],
#         "forward_connections": []
#     }
# }

# graph=Graph(layers)
# print(graph.graphs)