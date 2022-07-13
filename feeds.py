import json
import os
import pandas as pd


def prepare_write_hook(fpath, clear_file=False):
    if os.path.exists(fpath) and clear_file:
        os.remove(fpath)

    def write_callback(data):
        with open(fpath, 'a') as f:
            f.write(json.dumps(data, ensure_ascii=True) + '\n')
    return write_callback


def read_feed(fpath):
    df = pd.DataFrame()
    with open(fpath, 'r') as f:
        for line in f:
            row_data = json.loads(line)
            # print(row_data)
            df = df.append(row_data, ignore_index=True)
    return df


if __name__ == '__main__':
    print(read_feed('feed.json').head())
    # write_hook = prepare_write_hook('kek.json', clear_file=True)
    # for i in range(100):
    #     data = dict(a=i)
    #     write_hook(data)
