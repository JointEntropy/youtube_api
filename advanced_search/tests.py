import numpy as np
from logic import crawl, DataManager
from synthetic import spawn_feed_sampler, extract_videos, extract_channels


if __name__ == '__main__':
    np.random.seed(1)
    total_videos = np.arange(100000)
    total_channels = np.arange(100)

    N = total_videos.shape[0]
    video_pairs = np.c_[
        np.random.choice(total_channels, N, replace=True),
        np.random.choice(total_videos, N, replace=False)
    ]
    feed_sampler = spawn_feed_sampler(video_pairs)
    dm = DataManager()

    seed_video_id = 10

    crawl(seed_video_id, feed_sampler,
          extractors_pair=(extract_channels, extract_videos),
          data_manager=dm,
          log_each=20,
          max_iters=100)