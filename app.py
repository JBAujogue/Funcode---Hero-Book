import os
import pymupdf
import networkx as nx

import streamlit as st
import streamlit.components.v1 as components

from herobook.episode import get_episode_dict
from herobook.graph import build_nx_graph, convert_nx_to_nt_graph


path_to_repo = os.path.dirname(os.path.abspath(__file__))
path_to_data = os.path.join(path_to_repo, 'data')
path_to_pdfs = os.path.join(path_to_data, 'pdfs')
path_to_src  = os.path.join(path_to_repo, 'src')
path_to_html = os.path.join(path_to_data, 'plots', 'streamlit_graph.html')


def init_session_state():
    st.session_state.text = None
    st.session_state.path = None
    st.session_state.args = None
    st.session_state.html = None
    st.session_state.episodes = None
    st.session_state.nx_graph = None
    return


def solve_book(nx_graph, episodes):
    max_value = max(list(episodes.keys()))
    path = nx.shortest_path(nx_graph, source = 1, target = max_value)
    args = {arg: sum([
        (episodes[n][arg] not in [0, [], None, (0, 0)]) for n in path]) 
        for arg in episodes[1]
    }
    args = {k: v for k, v in args.items() if v}
    return (path, args)


def process_book():
    # load raw text
    file = st.session_state.file_uploader
    with pymupdf.open(stream = file.read(), filetype = "pdf") as doc:
        text = ''.join([page.get_text('text') for page in doc])

    # find episode markers & text
    episodes = get_episode_dict(text)

    # build graph
    nx_graph = build_nx_graph(episodes)

    # solve book
    path, args = solve_book(nx_graph, episodes)

    # store into session
    st.session_state.text = text
    st.session_state.path = path
    st.session_state.args = args
    st.session_state.episodes = episodes
    st.session_state.nx_graph = nx_graph
    return


def app():
    st.set_page_config(page_title = 'Hero Book Browser', layout = 'wide')
    st.title('Hero Book Browser')
    st.write(' ')
    st.write(' ')

    # init session state
    if 'text' not in st.session_state:
        init_session_state()

    # upload pdf file
    file = st.file_uploader(
        label = 'Upload a Hero Book:',
        type = ["pdf"],
        key = 'file_uploader',
        on_change = process_book,
    )

    if st.session_state.nx_graph is not None:
        text = st.session_state.text
        path = st.session_state.path
        args = st.session_state.args
        episodes = st.session_state.episodes
        nx_graph = st.session_state.nx_graph
        max_value = max(list(episodes.keys()))

        # solve book
        st.subheader('Suggested itinerary')
        st.write(' - '.join([str(i) for i in path]))

        st.write('**Events**')
        cols = st.columns(len(args))
        for i, arg in enumerate(args):
            col = cols[i]
            with col:
                st.write(arg, ':', args[arg])

        # browse book
        st.subheader('Browse the book')
        col_text, col_graph = st.columns(2)

        with col_text:
            source = st.number_input(
                label = 'Select an episode:',
                min_value = 1,
                max_value = max_value,
            )
            st.subheader('Episode {}'.format(source))
            st.write(episodes[source]['text'])
            st.subheader('Next options')
            st.write(' - '.join([str(i) for i in episodes[source]['targets']]))

        with col_graph:
            radius = st.number_input(
                label = 'Select an exploration radius:',
                value = 10,
                min_value = 1,
                max_value = 15,
            )
            lt_graph = nx.ego_graph(nx_graph, n = source, radius = radius)
            nt_graph = convert_nx_to_nt_graph(
                lt_graph, 
                node_colors = {source: '#fa624b'},
                height = '350pt',
                width = '100%',
            )
            nt_graph.save_graph(path_to_html)
            html = open(path_to_html, 'r', encoding = 'utf-8').read()

            st.write(' ')
            st.write(' ')
            components.html(html, height = 550)


if __name__ == '__main__':
    app()