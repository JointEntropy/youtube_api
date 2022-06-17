import requests
from loguru import logger
import json

class SearchStateManager:
    """
    Can save state for different search quiries.
    """
    pass


class SearchManager:
    base_url = 'https://youtube.googleapis.com/youtube/v3/search?'
    state_path = 'state.json'
    allowed_params = set(['order', 'type', 'q', 'regionCode',
                          'relevanceLanguage', 'maxResults',
                          'categoryId'
                          ])

    def __init__(self, config, save_search_state=False):
        self.config = config
        self.API_KEY = config['API_KEY']
        self.save_search_state = save_search_state
        self.next_page_token_ = None

    def channels_search(self, **kwargs):
        params = kwargs.copy()
        params.pop('type')
        self.search(type='channel', **kwargs)

    def search(self, total_results=None, next_page_token=None, **search_params):
        """
        If next_page_token is passed will try to continue scraping from this next page id.
        :param total_results:
        :param next_page_token:
        :param search_params:
        :return:
        """
        batch_id = 0
        search_params = search_params.copy()
        url = f'{SearchManager.base_url}part=id%2Csnippet&key={self.API_KEY}'
        url += '&' + '&'.join(SearchManager.construct_query_string(search_params))
        scraped_items_count = 0
        self.next_page_token_ = next_page_token
        if next_page_token:
            logger.info(f'Try continue search from page {self.next_page_token_}')
        while scraped_items_count < (total_results or 1):
            final_url = url + (f'&pageToken={self.next_page_token_}' if self.next_page_token_ else '')
            response = requests.get(final_url)
            data = response.json()
            if batch_id == 0:
                total_results = total_results or data['pageInfo']['totalResults']
            self.next_page_token_ = data.get('nextPageToken')
            for item in data['items']:
                yield item
                scraped_items_count += 1
            batch_id += 1
            if self.next_page_token_ is None:
                break
            if self.save_search_state:
                self.save_state(search_params, self.next_page_token_)

    @staticmethod
    def save_state(search_params, next_page_token):
        with open(SearchManager.state_path, 'w') as f:
            json.dump(dict(search_params=search_params,
                           next_page_token=next_page_token), f, indent=4)

    @staticmethod
    def load_state():
        with open(SearchManager.state_path, 'r') as f:
            state = json.load(f)
            next_page_token = state['next_page_token']
            search_params = state['search_params']
            return search_params, next_page_token

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
    sm = SearchManager(config, save_search_state=True)

    # new search
    search_params = {
        'regionCode': 'RU',
        'relevanceLanguage': 'ru',
        'q': 'спорт',
        'order': 'viewCount',  # 'videoCount',
        'type': 'channel',
        'maxResults': 25,
        # 'categoryId': 15
    }
    ## CContinue search
    next_page_token = 'CJYBEAA'
    # search_params, next_page_token = SearchManager.load_state()

    for item_search in sm.search(total_results=25, next_page_token=next_page_token, **search_params):
        print(item_search)


