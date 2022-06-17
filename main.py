from feeds import prepare_write_hook
from search_channels import SearchManager
from tqdm.auto import tqdm


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    sm = SearchManager(config, save_search_state=True)

    search_params = {
        'regionCode': 'RU',
        'relevanceLanguage': 'ru',
        'q': 'новости', #'блог', #'красота', #'кино', #'авто', #'музыка', #'игры', #'политика', #'спорт',
        'order': 'viewCount',  # 'videoCount',
        'type': 'channel',
        'maxResults': 50,
        # 'categoryId': 15
    }
    ## CContinue search
    next_page_token = None
    # search_params, next_page_token = SearchManager.load_state()

    write_hook = prepare_write_hook('feed.json')
    total_results = 2000
    for item in tqdm(sm.search(total_results=total_results, next_page_token=next_page_token, **search_params),
                     total=total_results):
        item['query'] = search_params
        write_hook(item)
