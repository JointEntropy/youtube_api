from logic import crawl, pop_from_stack, get_stack_len
from youtube_feed import youtube_feed_sampler


class DataManager:
    """
    Добавить логику скаченных
    """
    def __init__(self, all_known_channels):
        self.all_known_channels, self.all_known_videos = set(), set()

    def add_channels(self, new_channels):
        self.all_known_channels = self.all_known_channels | new_channels

    def add_videos(self, new_videos):
        self.all_known_videos = self.all_known_videos | new_videos


def start_exploring():
    start_key = '0dnLGoVYaz8'
    if get_stack_len():
        start_key = pop_from_stack()
    feed_sampler = youtube_feed_sampler()
    dm = DataManager()
    crawl(start_key, feed_sampler,
          extractors_pair=(lambda x: set(), lambda x: set(x)),
          data_manager=dm, log_each=1, max_iters=15)
    print(len(dm.all_known_videos))


if __name__ == '__main__':
    start_exploring()