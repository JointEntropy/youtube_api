import requests
from search_channels import SearchManager
import os

import json
os.environ['CONFIG_PATH'] = '../config.json'
with open(os.environ['CONFIG_PATH'], 'r') as f:
    config = json.load(f)


def youtube_feed_sampler():
    def get_feed(x: int, sample_size: int = 50) -> str:
        search_params = dict(relatedToVideoId=x,  type='video',
                             maxResults=min(sample_size, 50)
        )
        url = f'{SearchManager.base_url}key={config["API_KEY"]}'
        url += '&' + '&'.join(SearchManager.construct_query_string(search_params))
        data = requests.get(url).json()
        return list(map(lambda x: x['id']['videoId'], data.get('items', [])))
    return get_feed


def get_videos_meta_by_id(video_ids):
    def extract_litem_content(x):
        return dict(
            video_id=x['id'],
            data=dict((k, x[k]) for k in ['snippet', 'statistics'])
        )

    search_params = dict(id=','.join(video_ids),
                         part='snippet,contentDetails,statistics',)
    url = f'{SearchManager.video_url}key={config["API_KEY"]}'
    url += '&' + '&'.join(SearchManager.construct_query_string(search_params))
    data = requests.get(url).json()
    return list(map(extract_litem_content, data.get('items', [])))


if __name__ == '__main__':
    # print(youtube_feed_sampler()('XjPS56MCVK0'))
    print(json.dumps(get_videos_meta_by_id(['kWmso75aUWQ', 'Pbn7Ehvkq_0']), indent=3))