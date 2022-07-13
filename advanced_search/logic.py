from tqdm.auto import tqdm
from loguru import logger
from time import sleep
import redis
from youtube_feed import get_videos_meta_by_id
from typing import Union
import pandas as pd
import numpy as np


redis = redis.Redis(
    host='localhost',
    port='6379')

queue_key = 'youtube_crawler_queue'


def extract_content(key):
    items = set(c.decode('utf-8') for c in (redis.lrange(key, 0, end=redis.llen(key))))
    redis.delete(key)
    return items


def push_to_stack(key, items):
    if len(items)==0:
        return
    redis.lpush(key, *items)


def pop_from_stack(key):
    return redis.lpop(key).decode('utf-8')


def get_stack_len(key):
    return redis.llen(key)


def crawl(seed_video: str,
          feed_sampler: callable,
          data_manager,
          extractors_pair: Union[callable, callable],
          max_iters: int = 100,
          log_each: Union[int, None] = None
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
        # Make request to youtube and get new video candidates
        feed = feed_sampler(current_video)
        #
        true_new_videos = list(set(feed) - data_manager.all_known_videos)
        videos_meta = get_videos_meta_by_id(true_new_videos)
        data_manager.save_videos_meta(videos_meta)

        new_channels, new_videos = set(extract_channels(videos_meta)), set(extract_videos(videos_meta))

        # After getting meta info we can choose in which order we should push to stack.
        priorities = estimate_priorities(videos_meta, data_manager)
        sorted_new_videos = np.array(extract_videos(videos_meta))[priorities]
        push_to_stack(queue_key, sorted_new_videos)#, true_new_videos)

        # Add new entries ids to data manager
        data_manager.add_channels(new_channels)
        data_manager.add_videos(new_videos)

        # Select next candidate
        current_video = pop_from_stack(queue_key)
        iter_id += 1

        if log_each and iter_id % log_each == 0:
            logger.debug(f'Iter id: {iter_id}; VS: {get_stack_len(queue_key)}; '
                         f'KV: {len(data_manager.all_known_videos)}; KC: {len(data_manager.all_known_channels)}')


def estimate_priorities(feed_with_meta, data_manager):
    channels = np.array(list(map(lambda x: x['data']['snippet']['channelId'], feed_with_meta)))

    tmp = zip(channels, pd.Series(channels).duplicated())
    sort_idxs = np.argsort(list(map(lambda x: (x[0] in data_manager.all_known_channels) | (x[1]), tmp)))
    return sort_idxs
