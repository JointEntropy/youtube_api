from typing import Tuple, List
import networkx as nx
import pandas as pd
import numpy as np


def construct_graph_from_feed(feed_df: pd.DataFrame) -> nx.Graph:
    """
    Конвертирует feed записей из файла в граф связей с вершинами видео и каналами
    и связями для видео-канал и видео-видео(релевантные).
    """
    G = nx.Graph()
    for _, r in feed_df.iterrows():
        video_id = r['video_id']
        G.add_node(video_id, nodetype='video')
        if type(r['related'])==list:
            for rel_id in r['related']:
                G.add_node(rel_id, nodetype='video')
                G.add_edge(video_id, rel_id)
            continue
        channel_id = r['data']['snippet']['channelId']
        G.add_node(video_id, nodetype='video')
        G.add_node(channel_id, nodetype='channel')
        G.add_edge(video_id, channel_id, )
    return G


def add_rel_to_graph(G: nx.Graph,
                     node_id: str, rel_ids: List[str]) -> nx.Graph:
    """
    Добавляет связи релевантности между видео в графю.
    """
    for target_id in rel_ids:
        G.add_node(target_id, nodetype='video')
        G.add_edge(node_id, target_id)
    return G


def get_node_candidate(G: nx.Graph,
                       loss: callable = lambda x: x) -> Tuple[float, str]:
    """
    Ищет лучшую ноду-видео кандидата для продолжения исследования графа на очередном шаге.
    Возвращает скор(меньше - лучше) и id вершины.
    """
    # print('Any shit', list(f for f in G.nodes if (G.nodes[f].get('nodetype', None) is None)))
    for node_adg_info in G.adjacency():
        node_id = node_adg_info[0]
        node_ptr = G.nodes[node_id]
        if node_ptr.get('nodetype') != 'video':
            continue
        node_ptr['pow'] = len(node_adg_info[1])

    # print('Any shit', list(f for f in G.nodes if (G.nodes[f].get('nodetype', None) is None)))
    best_loss, best_id = float('inf'), -1
    for node_adg_info in G.adjacency():
        node_id = node_adg_info[0]
        node_ptr = G.nodes[node_id]
        if (node_ptr.get('nodetype') != 'video') or (node_ptr.get('bad', False)):
            continue
        node_score = sum([G.nodes[nbr_id]['pow'] for nbr_id
                          in node_adg_info[1] if G.nodes[nbr_id]['nodetype'] == 'video'])
        if loss(node_score) < best_loss:
            best_loss = loss(node_score)
            best_id = node_id
    return best_loss, best_id


def extract_videos(G):
    for node in G.nodes:
        if G.nodes[node].get('nodetype') == 'video':
            yield node


def extract_channels(G):
    for node in G.nodes:
        if G.nodes[node].get('nodetype') == 'channel':
            yield node