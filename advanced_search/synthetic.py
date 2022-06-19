import numpy as np


def spawn_feed_sampler(video_pairs):
    def get_feed(x, sample_size=10):
        # ignore x
        sampled_pairs_idxs = np.random.randint(low=0, high=len(video_pairs), size=sample_size)
        return video_pairs[sampled_pairs_idxs]
    return get_feed


def extract_channels(feed_data):
    return set(feed_data[:, 0])


def extract_videos(feed_data):
    return set(feed_data[:, 1])
