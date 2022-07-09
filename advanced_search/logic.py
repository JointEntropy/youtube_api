from tqdm.auto import tqdm
from loguru import logger

import redis

redis = redis.Redis(
    host='localhost',
    port='6379')

queue_key = 'youtube_crawler_queue'


def push_to_stack(items):
    redis.lpush(queue_key, *items)


def pop_from_stack():
    return redis.lpop(queue_key).decode('utf-8')


def get_stack_len():
    return redis.llen(queue_key)


def crawl(seed_video,
          feed_sampler,
          data_manager,
          extractors_pair,
          max_iters=100,
          log_each=None
          ):
    current_video = seed_video
    iter_id = 0

    # visit_stack = []
    iterator = tqdm(total=max_iters)

    extract_channels, extract_videos = extractors_pair
    while True:
        if iter_id >= max_iters:
            break
        iterator.update(1)
        feed = feed_sampler(current_video)
        new_channels, new_videos = extract_channels(feed), extract_videos(feed)

        push_to_stack(list(new_videos-data_manager.all_known_videos))
        #
        data_manager.add_channels(new_channels)
        data_manager.add_videos(new_videos)
        #
        current_video = pop_from_stack() # visit_stack.pop()
        iter_id += 1

        if log_each and iter_id % log_each == 0:
            logger.debug(f'Iter id: {iter_id}; VS: {get_stack_len()}; '
                         f'KV: {len(data_manager.all_known_videos)}; KC: {len(data_manager.all_known_channels)}')
