from abc import ABC, abstractmethod


class BaseExecutor(ABC):
    @abstractmethod
    def start_task(self, user_email, model_id, payload):
        raise NotImplementedError

    @abstractmethod
    def get_task_info(self, user_email, model_id):
        raise NotImplementedError

    @abstractmethod    
    def get_active_tasks(self, user_email):
        raise NotImplementedError        
    
