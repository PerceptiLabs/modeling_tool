from core_new.utils import LoopHook


class BaseControlApi:
    ''' EMPTY SHELL TO MOCK FUNCTIONALITY WHEN PROPAGATING THE NETWORK '''
    
    def epoch_loop(self):
        pass

    def training_iteration_loop(self, n_iterations):
        pass
    
    def validation_iteration_loop(self, n_iterations):
        pass
    
    def testing_iteration_loop(self, n_iterations):
        pass
    

class ControlApi(BaseControlApi):
    def __init__(self, state, ui):
        self._state = state
        self._ui = ui

    def epoch_loop(self, n_epochs):
        def on_create(n_epochs):
            self._state.init_epochs(n_epochs)

        def on_iterated(iteration):
            self._state.finish_epoch()
            self._ui.process()
        
        hook = LoopHook(range(n_epochs), max_iter=n_epochs,
                        on_create=on_create,
                        on_iterated=on_iterated)
        return hook
        
    def training_iteration_loop(self, n_iterations):
        def on_create(n_iters):
            self._state.init_training(n_iters)

        def on_iterated(iteration):
            self._state.finish_iteration()
            self._ui.process()            
        
        hook = LoopHook(range(n_iterations), max_iter=n_iterations,
                        on_create=on_create,
                        on_iterated=on_iterated)
        return hook
    
    def validation_iteration_loop(self, n_iterations):
        def on_create(n_iters):
            self._state.init_validation(n_iters)

        def on_iterated(iteration):
            self._state.finish_iteration()
            self._ui.process()                        
        
        hook = LoopHook(range(n_iterations), max_iter=n_iterations,
                        on_create=on_create,
                        on_iterated=on_iterated)
        return hook
    
    def testing_iteration_loop(self, n_iterations):
        def on_create(n_iters):
            self._state.init_testing(n_iters)

        def on_iterated(iteration):
            self._state.finish_iteration()
            self._ui.process()                        
        
        hook = LoopHook(range(n_iterations), max_iter=n_iterations,
                        on_create=on_create,
                        on_iterated=on_iterated)
        return hook
        

    
