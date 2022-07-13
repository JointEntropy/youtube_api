from logic import crawl, pop_from_stack, get_stack_len, extract_content, push_to_stack, queue_key
from youtube_feed import youtube_feed_sampler
from loguru import logger
from typing import List
import json


class DataManager:
    """
    Добавить логику скаченных
    """
    cache_videos = 'youtube_stored_key'
    cache_channels = 'youtube_channels_stored_key'

    def __init__(self, videos, channels):
        logger.debug(f'Loaded videos ids from redis: {len(videos)}')
        logger.debug(f'Loaded channels ids from redis: {len(channels)}')
        self.all_known_channels, self.all_known_videos = channels, videos

    def add_channels(self, new_channels):
        self.all_known_channels = self.all_known_channels | new_channels

    def add_videos(self, new_videos):
        self.all_known_videos = self.all_known_videos | new_videos

    def save_progress(self):
        logger.debug(f'Save videos progress. Collected element count: {len(self.all_known_videos)}')
        push_to_stack(DataManager.cache_videos, list(self.all_known_videos))
        logger.debug(f'Save channels progress. Collected element count: {len(self.all_known_channels)}')
        push_to_stack(DataManager.cache_channels, list(self.all_known_channels))

    def save_videos_meta(self, videos_meta_lst: List):
        with open('tempo_file.jsonl', 'a') as f:
            for item in videos_meta_lst:
                f.write(f'{json.dumps(item)}\n')


channels_extractors = lambda x: list(map(lambda x: x['data']['snippet']['channelId'], x))
videos_extractors = lambda x: list(map(lambda x: x['video_id'], x))


def start_exploring():
    start_key = '0dnLGoVYaz8'
    if get_stack_len(queue_key):
        start_key = pop_from_stack(queue_key)
    feed_sampler = youtube_feed_sampler()
    dm = DataManager(videos=extract_content(DataManager.cache_videos),
                     channels=extract_content(DataManager.cache_channels))

    try:
        crawl(start_key, feed_sampler,
              extractors_pair=(channels_extractors, videos_extractors),
              data_manager=dm, log_each=5, max_iters=10)
    finally:
        dm.save_progress()


if __name__ == '__main__':
    start_exploring()
