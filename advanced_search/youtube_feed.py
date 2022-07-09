import requests
from search_channels import SearchManager
import os

import json
os.environ['CONFIG_PATH'] = '../config.json'
with open(os.environ['CONFIG_PATH'], 'r') as f:
    config = json.load(f)


def youtube_feed_sampler():
    def get_feed(x: int, sample_size: int = 10) -> str:
        search_params = dict(relatedToVideoId=x,  type='video',
                             maxResults=min(sample_size, 50)
        )
        url = f'{SearchManager.base_url}key={config["API_KEY"]}'
        url += '&' + '&'.join(SearchManager.construct_query_string(search_params))
        data = requests.get(url).json()
        return list(map(lambda x: x['id']['videoId'], data['items']))
    return get_feed


if __name__ == '__main__':
    print(youtube_feed_sampler()('XjPS56MCVK0'))