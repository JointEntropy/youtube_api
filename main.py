from advanced_search.youtube_feed import youtube_feed_sampler
from advanced_search.clear_graph_explorer import GraphDataManager, graph_utils, crawl


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
