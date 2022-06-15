import requests

class SearchManager:
    base_url = 'https://youtube.googleapis.com/youtube/v3/search?'

    allowed_params = set(['order', 'type', 'q', 'regionCode',
                          'relevanceLanguage', 'maxResults',
                          'categoryId'
                          ])

    def __init__(self, config):
        self.config = config
        self.API_KEY = config['API_KEY']

    def channels_search(self, **kwargs):
        params = kwargs.copy()
        params.pop('type')
        self.search(type='channel', **kwargs)

    def search(self, total_results=None, **search_params):
        next_page_token = None
        batch_id = 0
        search_params = search_params.copy()
        url = f'{SearchManager.base_url}part=id%2Csnippet&key={self.API_KEY}'
        url += '&' + '&'.join(SearchManager.construct_query_string(search_params))
        scraped_items_count = 0
        while scraped_items_count < (total_results or 1):
            final_url = url + (f'&pageToken={next_page_token}' if next_page_token else '')
            response = requests.get(final_url)
            data = response.json()
            if batch_id == 0:
                total_results = total_results or data['pageInfo']['totalResults']
            next_page_token = data['nextPageToken']
            for item in data['items']:
                yield item
                scraped_items_count += 1
            batch_id += 1

    @staticmethod
    def construct_query_string(params):
        for param_key in params.keys():
            if param_key not in SearchManager.allowed_params:
                raise ValueError(f'Invalid param_key: `{param_key}` passed')
            param_query = f'{param_key}={params[param_key]}'
            yield param_query


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    sm = SearchManager(config)

    search_params = {
        'regionCode': 'RU',
        'relevanceLanguage': 'ru',
        'q': 'спорт',
        'order': 'viewCount',  # 'videoCount',
        'type': 'channel',
        'maxResults': 25,
        # 'categoryId': 15
    }
    for item_search in sm.search(total_results=25, **search_params):
        print(item_search)

