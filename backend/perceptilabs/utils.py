def dump_system_info(path):
    import multiprocessing
    import platform
    import time
    import json

    info = {}
    info['cpu_count'] = multiprocessing.cpu_count()
    info['time_zone'] = time.tzname
    
    info['platform'] = {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version()
    }

    with open(path, 'w') as f:
        json.dump(info, f, indent=4)

        
def dump_build_info(path):
    import json

    info = {}
    info['commit'] = ''
    info['version'] = ''    
    
    with open(path, 'w') as f:
        json.dump(info, f, indent=4)
