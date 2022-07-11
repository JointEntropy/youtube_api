import json
import pandas as pd


def parse_feed(fp):
    data_lst = []
    with open(fp, 'r') as f:
        for line in f:
            line = line.strip(']').strip('[').strip(',')
            data_lst.append(json.loads(line))
    return pd.DataFrame(data_lst)


if __name__ == '__main__':
    df = parse_feed('tempo_file.jsonl')