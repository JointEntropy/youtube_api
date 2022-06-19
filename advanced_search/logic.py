from tqdm.auto import tqdm
from time import sleep
from loguru import logger


def crawl(seed_video,
          feed_sampler,
          data_manager,
          extractors_pair,
          max_iters=100,
          log_each=None
          ):
    current_video = seed_video
    iter_id = 0

    visit_stack = []
    iterator = tqdm(total=max_iters)

    extract_channels, extract_videos = extractors_pair
    while True:
        if iter_id >= max_iters:
            break
        iterator.update(1)
        feed = feed_sampler(current_video)
        new_channels, new_videos = extract_channels(feed), extract_videos(feed)

        #
        data_manager.add_channels(new_channels)
        data_manager.add_videos(new_videos)
        #
        visit_stack.extend(new_videos)
        current_video = visit_stack.pop()
        iter_id += 1

        if log_each and iter_id % log_each == 0:
            logger.debug(f'Iter id: {iter_id}; VS: {len(visit_stack)}; '
                         f'KV: {len(data_manager.all_known_videos)}; KC: {len(data_manager.all_known_channels)}')
