import threading


class StateTransitionError(Exception):
    pass


class State:
    INITIALIZING = 'initializing'    
    READY = 'ready'    
    TRAINING_PAUSED = 'training-paused'
    TRAINING_PAUSED_HEADLESS = 'training-paused-headless'    
    TRAINING_RUNNING = 'training-running'
    TRAINING_RUNNING_HEADLESS = 'training-running-headless'    
    TRAINING_COMPLETED = 'training-completed'
    TRAINING_STOPPED = 'training-stopped'
    TRAINING_TIMEOUT = 'training-timeout'
    TRAINING_FAILED = 'training-failed'
    CLOSING = 'closing'

    idle_states = (
        READY,
        TRAINING_PAUSED,
        TRAINING_PAUSED_HEADLESS,
        TRAINING_COMPLETED,
        TRAINING_STOPPED
    )
    done_states = (
        TRAINING_COMPLETED,
        TRAINING_STOPPED
    )
    exit_states = (
        CLOSING,
        TRAINING_TIMEOUT,
        TRAINING_FAILED
    )
    running_states = (
        TRAINING_RUNNING,
        TRAINING_RUNNING_HEADLESS
    )
    paused_states = (
        TRAINING_PAUSED,
        TRAINING_PAUSED_HEADLESS
    )
    active_states = running_states + paused_states

    
    allowed_transitions = (
        (INITIALIZING, READY),
        (READY, TRAINING_RUNNING),
        (READY, TRAINING_FAILED),
        (READY, TRAINING_STOPPED),        
        (TRAINING_RUNNING, TRAINING_TIMEOUT),
        (TRAINING_RUNNING, TRAINING_FAILED),
        (TRAINING_RUNNING, TRAINING_COMPLETED),
        (TRAINING_RUNNING, TRAINING_PAUSED),
        (TRAINING_RUNNING, TRAINING_STOPPED),
        (TRAINING_RUNNING, TRAINING_RUNNING_HEADLESS),
        (TRAINING_RUNNING_HEADLESS, TRAINING_TIMEOUT),
        (TRAINING_RUNNING_HEADLESS, TRAINING_FAILED),
        (TRAINING_RUNNING_HEADLESS, TRAINING_COMPLETED),
        (TRAINING_RUNNING_HEADLESS, TRAINING_PAUSED_HEADLESS),
        (TRAINING_RUNNING_HEADLESS, TRAINING_STOPPED),
        (TRAINING_RUNNING_HEADLESS, TRAINING_RUNNING),                                
        (TRAINING_PAUSED, TRAINING_RUNNING),
        (TRAINING_PAUSED, TRAINING_STOPPED),
        (TRAINING_PAUSED, TRAINING_PAUSED_HEADLESS),
        (TRAINING_PAUSED_HEADLESS, TRAINING_RUNNING_HEADLESS),
        (TRAINING_PAUSED_HEADLESS, TRAINING_PAUSED),
        (TRAINING_COMPLETED, CLOSING),
        (TRAINING_RUNNING, CLOSING),
        (TRAINING_PAUSED, CLOSING),
        (TRAINING_STOPPED, CLOSING),        
        (TRAINING_RUNNING_HEADLESS, CLOSING),
        (TRAINING_PAUSED_HEADLESS, CLOSING),                                
        (TRAINING_TIMEOUT, CLOSING),
        (TRAINING_FAILED, CLOSING),
        (READY, CLOSING)
    )
    
    def __init__(self, on_transition=None):
        self._state = self.INITIALIZING
        self._lock = threading.Lock()
        self._on_transition = on_transition

    @property
    def value(self):
        return self._state

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
    
    def transition(self, new_state):
        if new_state is None:
            return        
        if self._state == new_state:
            return
        
        with self._lock: 
            if (self._state, new_state) in self.allowed_transitions:
                self._state = new_state
            else:
                raise StateTransitionError(f"Cannot transition from '{self._state}' to '{new_state}'")
            if self._on_transition:
                self._on_transition(new_state)
                
    @classmethod
    def visualize(cls):
        import matplotlib.pyplot as plt
        import networkx as nx
        graph = nx.DiGraph()
        
        x = list(cls.allowed_transitions)
        graph.add_edges_from(x)
        pos = nx.shell_layout(graph)
        #pos = nx.circular_layout(graph)    
        nx.draw(graph, pos, with_labels=True)
        plt.show()
        

if __name__ == "__main__":
    State.visualize()
        
