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


class DataManager:
    def __init__(self):
        self.all_known_channels, self.all_known_videos = set(), set()

    def add_channels(self, new_channels):
        self.all_known_channels = self.all_known_channels | new_channels

    def add_videos(self, new_videos):
        self.all_known_videos = self.all_known_videos | new_videos
