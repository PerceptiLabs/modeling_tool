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


def stringify(obj, max_len=70, new_lines=False, indent=0, sort=False):
    def _format(value):
        value_str = str(value)
        if not new_lines:
            value_str = value_str.replace('\n', '')            
        if len(value_str) > max_len:
            value_str = value_str[0:max_len] + '...'
        value_str = f'{value_str} [{type(value).__name__}]'            
        return value_str

    def search(obj, path=''):
        if type(obj) in [list, tuple, set]:
            nesting = any(type(x) in [list, tuple, set, dict] for x in obj)
            if nesting and len(str(obj).replace('\n', '')) > max_len:            
                for i, o in enumerate(obj):
                    search(o, path=f'{path}/{i}')
            else:
                val_str = _format(obj)                
                pairs.append((path+'/', val_str))
                
        elif isinstance(obj, dict):
            if len(str(obj).replace('\n', '')) > max_len:
                for k, o in obj.items():
                    search(o, path=f'{path}/{k}')
            else:
                val_str = _format(obj)
                pairs.append((path+'/', val_str))
        else:
            val_str = _format(obj)                            
            pairs.append((path, val_str))
            
    pairs = []
    search(obj)
    
    text = ''
    n_chars = max(len(p) for p, _ in pairs)

    if sort:
        pairs = sorted(pairs, key=lambda x: x[0])
    
    for path, value in pairs:
        text += ' '*indent + path.ljust(n_chars, ' ') + ' : ' + value + '\n'
                          
    return text
    

if __name__ == "__main__":
    import numpy as np
    obj = {
        'hello': '123456',
        'hehe': {
            'bla': [213,]*10,
            'zzz': np.random.random((25, 323))
        }
    }    
    x = stringify(obj)
    print(x)
