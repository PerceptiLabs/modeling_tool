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
            backward_connections_list = [i[0] for i in self.graph[Id]["backward_connections"]]
            #print(backward_connections_list)
            if not set(backward_connections_list).issubset(list(visited.keys())):
                if not queue:
                    pass
                else:
                    queue.append(Id)
            elif Id not in visited:
                visited[Id]=dict(Con=backward_connections_list,Info=graph[Id],Copy=False)
                forward_connections_list = [i[0] for i in graph[Id]["forward_connections"]]
                for for_con in forward_connections_list:
                    if for_con not in queue:
                        queue.append(for_con)
                # queue.extend(graph[Id]["forward_connections"])
        if any([True for Id in end_points if (visited[Id]['Info']['Type']=='TrainReinforce' and visited[Id]['Info']['Properties'])]):
            visited=self.manipulate_graph(visited,start,end_points)
        return visited

    def manipulate_graph(self,graph,start_points,end_points):
        # print(graph)
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
                            if graph[Id]['Info']['backward_connections'][0][0] in start_points:
                                data_id=graph[Id]['Info']['backward_connections']
                                
                                newGraph[str(maxId+int(Id))]=dict(Con=[data_id[0][0]],Info=graph[Id]['Info'],Copy=True,CopyOf=Id)
                                self.copykeys.append(str(maxId+int(Id)))
                                #newGraph[str(maxId+int(Id))]=dict(Con=[],Info=graph[Id]['Info'],Copy=True)
                            elif graph[Id]['Info']['forward_connections'][0][0] in end_points:
                                newGraph[str(maxId+int(Id))]=dict(Con=[str(int(con[0])+maxId) for con in graph[Id]['Info']["backward_connections"]],Info=graph[Id]['Info'],Copy=True,CopyOf=Id,Input_ref=data_id)
                                newGraph[endId]['Con'].append(str(maxId+int(Id)))
                                self.copykeys.append(str(maxId+int(Id)))
                            else:
                                newGraph[str(maxId+int(Id))]=dict(Con=[str(int(con[0])+maxId) for con in graph[Id]['Info']["backward_connections"]],Info=graph[Id]['Info'],CopyOf=Id,Copy=True)
                                self.copykeys.append(str(maxId+int(Id)))
                    newGraph.pop(endId)
                    newGraph[endId]=graph[endId]
                    online_net = None
                    target_net = None
                    layer_pairs = []
                    for id_ in newGraph:
                        copied_id = newGraph[id_].get('CopyOf')
                        if copied_id is None:
                            # copied_id_name = ''
                            # id_name = ''
                            # online_net = copied_id_name
                            # target_net = id_name
                            continue
                        copied_id_name = graph[copied_id]['Info']['Name'] 
                        id_name = newGraph[id_]['Info']['Name'] 
                        layer_pairs.append((copied_id_name, id_name))

                        if copied_id in newGraph[endId]['Con']:
                            online_net = copied_id_name
                            target_net = id_name
                            newGraph[endId]['Con'].append(id_) # TODO: is backwards connections needed too?
                    
                    if online_net is None:
                        online_net = 'missing incoming connections'
                        target_net = 'missing incoming connections'
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
    # layerdict = {'1575248223920': {'Name': 'mnist', 'Type': 'LayerCustom', 'checkpoint': [], 'endPoints': [], 'Properties': {}, 'Code': {'Output': 'Y = tf.random.normal([10,784], mean=0, stddev=1.0)\n\nY = tf.convert_to_tensor(Y, dtype=tf.float32)\n\n'}, 'backward_connections': [], 'forward_connections': [['1576165220661', 'generator']]}, '1575281113420': {'Name': 'noise input', 'Type': 'LayerCustom', 'checkpoint': [], 'endPoints': [], 'Properties': {}, 'Code': {'Output': 'Y = tf.random.normal([10,100], mean=0, stddev=1.0)'}, 'backward_connections': [], 'forward_connections': [['1575281171340', 'Fully Connected_1'], ['1576796254554', 'Layer Custom_1']]}, '1575281171340': {'Name': 'Fully Connected_1', 'Type': 'DeepLearningFC', 'checkpoint': [], 'endPoints': [], 'Properties': {'Neurons': '128', 'Activation_function': 'ReLU', 'Dropout': False, 'Keep_prob': '1'}, 'Code': {'Output': "with tf.variable_scope('gen',reuse=True):\n  input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]\n  shape = [input_size, 128]\n  initial = tf.truncated_normal(shape, stddev=0.1)\n  W = tf.Variable(initial, name='weights-1575281171340')\n  initial = tf.constant(0.1, shape=[128])\n  b = tf.Variable(initial, name='bias-1575281171340')\n  flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)\n  node = tf.matmul(flat_node, W)\n  node = node + b\n\n  Y = tf.nn.relu(node)\n"}, 'backward_connections': [['1575281113420', 'noise input']], 'forward_connections': [['1575281177664', 'Fully Connected_2']]}, '1575281177664': {'Name': 'Fully Connected_2', 'Type': 'DeepLearningFC', 'checkpoint': [], 'endPoints': [], 'Properties': {'Neurons': '128', 'Activation_function': 'ReLU', 'Dropout': False, 'Keep_prob': '1'}, 'Code': {'Output': "with tf.variable_scope('gen',reuse=True):\n  input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]\n  shape = [input_size, 128]\n  initial = tf.truncated_normal(shape, stddev=0.1)\n  W = tf.Variable(initial, name='weights-1575281177664')\n  initial = tf.constant(0.1, shape=[128])\n  b = tf.Variable(initial, name='bias-1575281177664')\n  flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)\n  node = tf.matmul(flat_node, W)\n  node = node + b\n\n  Y = tf.nn.relu(node)\n"}, 'backward_connections': [['1575281171340', 'Fully Connected_1']], 'forward_connections': [['1575281182231', 'Fully Connected_3']]}, '1575281182231': {'Name': 'Fully Connected_3', 'Type': 'DeepLearningFC', 'checkpoint': [], 'endPoints': [], 'Properties': {'Neurons': '784', 'Activation_function': 'Tanh', 'Dropout': False, 'Keep_prob': '1'}, 'Code': {'Output': "with tf.variable_scope('gen',reuse=True):\n  input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]\n  shape = [input_size, 784]\n  initial = tf.truncated_normal(shape, stddev=0.1)\n  W = tf.Variable(initial, name='weights-1575281182231')\n  initial = tf.constant(0.1, shape=[784])\n  b = tf.Variable(initial, name='bias-1575281182231')\n  flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)\n  node = tf.matmul(flat_node, W)\n  node = node + b\n\n  Y = tf.tanh(node)\n"}, 'backward_connections': [['1575281177664', 'Fully Connected_2']], 'forward_connections': [['1576165220661', 'generator']]}, '1575281546407': {'Name': 'Fully Connected_4', 'Type': 'DeepLearningFC', 'checkpoint': [], 'endPoints': [], 'Properties': {'Neurons': '128', 'Activation_function': 'ReLU', 'Dropout': False, 'Keep_prob': '1'}, 'Code': {'Output': "with tf.variable_scope('dis',reuse=True):\n  input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]\n  shape = [input_size, 128]\n  initial = tf.truncated_normal(shape, stddev=0.1)\n  W = tf.Variable(initial, name='weights-1575281546407')\n  initial = tf.constant(0.1, shape=[128])\n  b = tf.Variable(initial, name='bias-1575281546407')\n  flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)\n  node = tf.matmul(flat_node, W)\n  node = node + b\n\n  Y = tf.nn.relu(node)\n  g_out = X['Y']\n"}, 'backward_connections': [['1576165220661', 'generator']], 'forward_connections': [['1575281557455', 'Fully Connected_5']]}, '1575281557455': {'Name': 'Fully Connected_5', 'Type': 'DeepLearningFC', 'checkpoint': [], 'endPoints': [], 'Properties': {'Neurons': '128', 'Activation_function': 'ReLU', 'Dropout': False, 'Keep_prob': '1'}, 'Code': {'Output': "with tf.variable_scope('dis',reuse=True):\n  input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]\n  shape = [input_size, 128]\n  initial = tf.truncated_normal(shape, stddev=0.1)\n  W = tf.Variable(initial, name='weights-1575281557455')\n  initial = tf.constant(0.1, shape=[128])\n  b = tf.Variable(initial, name='bias-1575281557455')\n  flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)\n  node = tf.matmul(flat_node, W)\n  node = node + b\n\n  Y = tf.nn.relu(node)\n  g_out = X['g_out']\n"}, 'backward_connections': [['1575281546407', 'Fully Connected_4']], 'forward_connections': [['1575281567134', 'Fully Connected_6']]}, '1575281567134': {'Name': 'Fully Connected_6', 'Type': 'DeepLearningFC', 'checkpoint': [], 'endPoints': [], 'Properties': {'Neurons': '1', 'Activation_function': 'Sigmoid', 'Dropout': False, 'Keep_prob': '1'}, 'Code': {'Output': "with tf.variable_scope('dis',reuse=True):\n  input_size = np.cumprod(X['Y'].get_shape().as_list()[1:])[-1]\n  shape = [input_size, 1]\n  initial = tf.truncated_normal(shape, stddev=0.1)\n  W = tf.Variable(initial, name='weights-1575281567134')\n  initial = tf.constant(0.1, shape=[1])\n  b = tf.Variable(initial, name='bias-1575281567134')\n  flat_node = tf.cast(tf.reshape(X['Y'], [-1, input_size]), dtype=tf.float32)\n  node = tf.matmul(flat_node, W)\n  node = node + b\n\n  Y = node\n  g_out = X['g_out']\n"}, 'backward_connections': [['1575281557455', 'Fully Connected_5']], 'forward_connections': [['1575297088753', 'Layer Custom_2']]}, '1575282485879': {'Name': 'GAN train ', 'Type': 'LayerCustom', 'checkpoint': [], 'endPoints': [], 'Properties': {}, 'Code': {'Output': "api.data.store_locals(locals())\n\nD_logits_real = X['Y_real_sigmoid']\nD_logits_fake = X['Y_fake_sigmoid']\n\ndef loss():\n\treturn 1.\n\n#D_real_loss = loss_func(D_logits_real,tf.ones_like(D_logits_real)*0.9) \n#D_fake_loss = loss_func(D_logits_fake,tf.zeros_like(D_logits_real))\n\ndef D_loss(D_logits_real, D_logits_fake):\n\treturn tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logits_real,labels=tf.ones_like(D_logits_real)*0.9)) + tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logits_fake,labels=tf.zeros_like(D_logits_real)))\n\ndef G_loss(D_logits_fake):\n\treturn tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logits_fake,labels=D_logits_fake))\n\ngradients = {}\nfor var in tf.trainable_variables():\n    name = 'grad-' + var.name\n    gradients[name] = tf.gradients(loss, [var])\nprint(gradients)\n\ntvars=tf.trainable_variables()  #returns all variables created(the two variable scopes) and makes trainable true\nd_vars=[var for var in tvars if 'dis' in var.name]\ng_vars=[var for var in tvars if 'gen' in var.name]\n\nprint(tvars)\nlr = 0.001\n\n#D_trainer=tf.train.AdamOptimizer(lr).minimize(loss)\n#G_trainer=tf.train.AdamOptimizer(lr).minimize(loss, var_list = g_vars)\n\nbatch_size=100\nepochs=100\ninit=tf.global_variables_initializer()\nsamples=[] #generator examples\n\n"}, 'backward_connections': [['1575297088753', 'Layer Custom_2']], 'forward_connections': []}, '1575297088753': {'Name': 'Layer Custom_2', 'Type': 'LayerCustom', 'checkpoint': [], 'endPoints': [], 'Properties': {}, 'Code': {'Output': "\nY_real = X['Y'][:10,:]\nY_fake = X['Y'][10:,:]\ng_out = X['g_out']\nY_real_sigmoid = tf.sigmoid(Y_real)\nY_fake_sigmoid = tf.sigmoid(Y_fake)\n\n"}, 'backward_connections': [['1575281567134', 'Fully Connected_6']], 'forward_connections': [['1575282485879', 'GAN train ']]}, '1576165220661': {'Name': 'generator', 'Type': 'LayerCustom', 'checkpoint': [], 'endPoints': [], 'Properties': {}, 'Code': {'Output': "Y = None\nfor key in X.keys():\n  if Y is None:\n    Y = X[key]['Y']\n  else:\n    Y = tf.concat([Y, X[key]['Y']], 0)\n    \n"}, 'backward_connections': [['1575281182231', 'Fully Connected_3'], ['1575248223920', 'mnist']], 'forward_connections': [['1575281546407', 'Fully Connected_4']]}, '1576796254554': {'Name': 'Layer Custom_1', 'Type': 'LayerCustom', 'checkpoint': [], 'endPoints': [], 'Properties': {}, 'Code': {'Output': 'print(X.keys())'}, 'backward_connections': [['1575281113420', 'noise input']], 'forward_connections': []}}
    # graph = Graph(layerdict)
    import json
    path = '/Users/mukund/Desktop/templates/Image Classification/model.json'
    with open(path, 'r') as f:
        json_network = json.load(f)
    print(json_network['networkElementList'].keys())
    graph = Graph(json_network['networkElementList'])
    print(graph.graph.items)


