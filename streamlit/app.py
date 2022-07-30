import os
import sys
from io import open, BytesIO, StringIO

# text
import fitz

# graph
import networkx as nx

# UI
import streamlit as st
import streamlit.components.v1 as components


# path_to_repo = os.path.dirname(os.getcwd())
path_to_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_to_data = os.path.join(path_to_repo, 'data')
path_to_pdfs = os.path.join(path_to_data, 'pdfs')
path_to_src  = os.path.join(path_to_repo, 'src')
path_to_html = os.path.join(path_to_data, 'plots', 'streamlit_graph.html')

# custom imports
sys.path.insert(0, path_to_src)

from herobook.episode import get_episode_dict
from herobook.graph   import build_nx_graph, convert_nx_to_nt_graph



#**********************************************************
#*                      functions                         *
#**********************************************************

def init_session_state():
    st.session_state.text     = None
    st.session_state.episodes = None
    st.session_state.nx_graph = None
    st.session_state.html     = None
    return
 


def process_book():
    # load raw text
    file = st.session_state.file_uploader
    with fitz.open(stream = file.read(), filetype = "pdf") as doc:
        text = [page.get_text('text') for page in doc]
        text = ''.join(text)

    # find episode markers & text
    episodes = get_episode_dict(text)

    # build graph
    nx_graph = build_nx_graph(episodes)
    
    # store into session
    st.session_state.text     = text
    st.session_state.episodes = episodes
    st.session_state.nx_graph = nx_graph
    return





#**********************************************************
#                      main script                        *
#**********************************************************
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
	episodes = st.session_state.episodes
	nx_graph = st.session_state.nx_graph

	# solve book
	max_value = max(list(episodes.keys()))
	path = nx.shortest_path(st.session_state.nx_graph, source = 1, target = max_value)
	st.subheader('Suggested itinerary')
	st.write(' - '.join([str(i) for i in path]))


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
	

    

