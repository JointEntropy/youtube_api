from feeds import prepare_write_hook
from search_channels import SearchManager

if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    sm = SearchManager(config)

    search_params = {
        'regionCode': 'RU',
        'relevanceLanguage': 'ru',
        'q': 'кино', #'авто', #'музыка', #'игры', #'политика', #'спорт',
        'order': 'viewCount',  # 'videoCount',
        'type': 'channel',
        'maxResults': 50,
        # 'categoryId': 15
    }

    write_hook = prepare_write_hook('feed.json')

    for item in sm.search(total_results=250, **search_params):
        item['query'] = search_params
        write_hook(item)
