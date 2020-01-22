



if __name__ == "__main__":
    DISTRIBUTED = True
    EPOCHS = 2
    NET_PATH = 'the_net.json'

    import queue
    import json
    from core_new.core import *    
    from core_new.errors import CoreErrorHandler
    from core_new.history import SessionHistory
    from core_new.data import DataContainer
    from core_new.cache import get_cache
    from core_new.core_distr import DistributedCore
    from codehq import CodeHqNew as CodeHq
    from modules import ModuleProvider    
    import logging

    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.INFO)
    
    errorQueue=queue.Queue()
    commandQ=queue.Queue()
    resultQ=queue.Queue()    

    with open(NET_PATH, 'r') as f:
        network = json.load(f)

    network['Layers']['1564399790363']['Properties']['Distributed'] = DISTRIBUTED
    network['Layers']['1564399790363']['Properties']['Epochs'] = str(EPOCHS)    
    
    graphObj = Graph(network['Layers'])
    graph_dict=graphObj.graphs

    data_container = DataContainer()
    error_handler = CoreErrorHandler(errorQueue)

    module_provider = ModuleProvider()
    module_provider.load('tensorflow', as_name='tf')
    module_provider.load('numpy', as_name='np')
    module_provider.load('pandas', as_name='pd')
    module_provider.load('gym')
    module_provider.load('json')       
    module_provider.load('os')  
    module_provider.load('skimage')
    module_provider.load('dask.array', as_name='da')
    module_provider.load('dask.dataframe', as_name='dd')
    
    cache = get_cache()
    session_history = SessionHistory(cache)
    session_proc_handler = SessionProcessHandler(graph_dict, data_container, commandQ, resultQ)
    
    if DISTRIBUTED:
        core = DistributedCore(CodeHq, graph_dict, data_container, session_history, module_provider,
                               error_handler, session_proc_handler, checkpointValues=None)
        
        core.run()        
        print("resultQ size", resultQ.qsize())

        assert resultQ.qsize() == 3000

        import pdb; pdb.set_trace()
        
    else:
        core = Core(CodeHq, graph_dict, data_container, session_history, module_provider,
                    error_handler, session_proc_handler, checkpointValues=None) 
        core.run()


        print("resultQ size", resultQ.qsize())
        assert resultQ.qsize() == 3000
    

        import pdb; pdb.set_trace()
