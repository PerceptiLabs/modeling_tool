import time
import threading
import psutil
import GPUtil
import math


class HardwareStats:
    def __init__(self, refresh_interval=3):
        self.cpu_usage = 0
        self.gpu_usage = 0        
        self.mem_usage = 0        
        
        self._refresh_interval = refresh_interval

        thread = threading.Thread(target=self._worker, daemon=True)
        thread.start()

    def _get_cpu_usage(self):
        cpu = psutil.cpu_percent()
        return cpu

    def _get_mem_usage(self):
        mem = dict(psutil.virtual_memory()._asdict())["percent"]    
        return mem

    def _get_gpu_usage(self):
        gpus = GPUtil.getGPUs()
        per_gpu_load = [gpu.load*100 if not math.isnan(gpu.load) else 0 for gpu in gpus]
    
        if not per_gpu_load:
            return ""

        average_load = sum(per_gpu_load)/len(per_gpu_load)
    
        if int(average_load) == 0:
            average_load = 1
        
        return average_load

    def _worker(self):
        while True:
            self.cpu_usage = self._get_cpu_usage()
            self.gpu_usage = self._get_gpu_usage()            
            self.mem_usage = self._get_mem_usage()                  
            time.sleep(self._refresh_interval)



