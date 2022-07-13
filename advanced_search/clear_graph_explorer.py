import graph_utils

from tqdm.auto import tqdm
from loguru import logger

from youtube_feed import get_videos_meta_by_id
from typing import Union, List, Dict
from advanced_search.parse_feed import parse_feed
import json
from advanced_search.youtube_feed import youtube_feed_sampler
import networkx as nx
import os


channels_extractors = lambda x: list(map(lambda x: x['data']['snippet']['channelId'], x))
videos_extractors = lambda x: list(map(lambda x: x['video_id'], x))


class GraphDataManager:
    """
    Добавить логику скаченных
    """
    def __init__(self, feed_path: Union[str, None]):
        self.G = nx.Graph()
        if feed_path and os.path.exists(feed_path):
            logger.debug(f'Using existing feed data on path {feed_path} to build graph')
            feed_data = parse_feed(feed_path)
            self.G = graph_utils.construct_graph_from_feed(feed_data)
        self.feed_path = feed_path
        videos, channels = list(graph_utils.extract_videos(self.G)), list(graph_utils.extract_channels(self.G))
        logger.debug(f'Loaded videos count: {len(videos)}')
        logger.debug(f'Loaded channels count: {len(channels)}')
        self.all_known_channels, self.all_known_videos = set(channels), set(videos)

    def mark_bad_node(self, bad_node):
        self.G.nodes[bad_node]['bad'] = True

    def update_graph(self, current_node: str, feed: List[str]) -> None:
        # Get meta info for new videos
        # print('Any shit update1', list(f for f in self.G.nodes if (self.G.nodes[f].get('nodetype', None) is None)))
        new_feed = list(set(feed) - self.all_known_videos)
        new_feed_meta = get_videos_meta_by_id(new_feed)

        # Exract clear ids from new feed meta
        # print('Any shit update2', list(f for f in self.G.nodes if (self.G.nodes[f].get('nodetype', None) is None)))
        new_channels, new_videos = channels_extractors(new_feed_meta), videos_extractors(new_feed_meta)
        self._add_video_channel_pairs(self.G, new_videos, new_channels)

        # Add to collections
        self.all_known_channels = self.all_known_channels | set(new_channels)
        self.all_known_videos = self.all_known_videos | set(new_videos)

        # Save relevance info on the original data so all new edges will be stored(even for existing nodes).
        # print('Any shit update3', list(f for f in self.G.nodes if (self.G.nodes[f].get('nodetype', None) is None)))
        ### Тут происходит залупонь
        graph_utils.add_rel_to_graph(self.G, current_node, feed)

        # Save progress to feed file

        self.save_relevance_meta(self.feed_path, dict(video_id=current_node, related=feed))
        self.save_videos_meta(self.feed_path, new_feed_meta)
        ### Тут кончается залупонь
        # print('Any shit update4', list(f for f in self.G.nodes if (self.G.nodes[f].get('nodetype', None) is None)))

    @staticmethod
    def _add_video_channel_pairs(G: nx.Graph,
                                 videos: List[str], channels: List[str]) -> None:
        # Add new nodes first
        for video in videos:
            G.add_node(video, nodetype='video')
        for channel in channels:
            G.add_node(channel, nodetype='channel')
        for video, channel in zip(videos, channels):
            G.add_edge(video, channel)

    def find_candidate(self) -> str:
        score, candidate_video_id = graph_utils.get_node_candidate(self.G)
        return candidate_video_id

    @staticmethod
    def save_videos_meta(fpath, videos_meta_lst: List) -> None:
        with open(fpath, 'a') as f:
            for item in videos_meta_lst:
                f.write(f'{json.dumps(item)}\n')

    @staticmethod
    def save_relevance_meta(fpath, relavance_info: dict) -> None:
        with open(fpath, 'a') as f:
            f.write(f'{json.dumps(relavance_info)}\n')


def crawl(seed_video: str,
          feed_sampler: callable,
          data_manager: GraphDataManager,
          max_iters: int = 100,
          log_each: Union[int, None] = None
    ):
    current_video = seed_video
    iter_id = 0

    iterator = tqdm(total=max_iters)
    while True:
        if iter_id >= max_iters:
            break
        iterator.update(1)
        # Make request to youtube and get new video candidates
        feed = feed_sampler(current_video)
        if len(feed) == 0:
            data_manager.mark_bad_node(current_video)
        else:
            data_manager.update_graph(current_node=current_video, feed=feed)
        # Select next candidate
        current_video = data_manager.find_candidate()
        iter_id += 1

        if log_each and iter_id % log_each == 0:
            logger.debug(f'Iter id: {iter_id};'
                         f'KV: {len(data_manager.all_known_videos)}; KC: {len(data_manager.all_known_channels)}')


def start_exploring(start_key=None):
    feed_sampler = youtube_feed_sampler()
    feed_path = 'graph_feed.jsonl'
    data_manager = GraphDataManager(feed_path)
    start_key = start_key or graph_utils.get_node_candidate(data_manager.G)
    crawl(start_key, feed_sampler, log_each=5, max_iters=100,
          data_manager=data_manager)


if __name__ == '__main__':
    start_exploring(start_key = '0dnLGoVYaz8')
    # start_exploring()
