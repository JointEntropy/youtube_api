import json
import os


def prepare_write_hook(fpath, clear_file=False):
    if os.path.exists(fpath) and clear_file:
        os.remove(fpath)

    def write_callback(data):
        with open(fpath, 'a') as f:
            f.write(json.dumps(data) + '\n')
    return write_callback


if __name__ == '__main__':
    write_hook = prepare_write_hook('kek.json', clear_file=True)
    for i in range(100):
        data = dict(a=i)
        write_hook(data)
