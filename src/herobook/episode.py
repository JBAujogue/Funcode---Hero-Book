
import sys
import os
from io import open, BytesIO, StringIO
import re

# data
import pandas as pd





#**********************************************************
#*                       content                          *
#**********************************************************

def get_episode_dict(text):
    # split into lines
    lines = text.split('\n')

    # find episode markers
    episode_markers = find_episode_markers_from_lines(lines)
    episode_idx, episode_ids = [list(m) for m in zip(*episode_markers)]

    # init episode_dict
    episode_dict = {i: dict() for i in episode_ids}

    # find episode texts
    for i, e1, e2 in zip(episode_ids, episode_idx, episode_idx[1:] + [len(lines)]):
        ep_text = '\n'.join([l.strip() for l in lines[e1+1: e2]]).strip()
        ep_text = re.sub('\n(\n)+', '. ', ep_text)
        ep_text = re.sub('(\.)+', '.', ep_text)
        ep_text = re.sub('(\n)+', ' ', ep_text)
        episode_dict[i]['text'] = ep_text

    # find episode target ids
    for i in episode_dict:
        episode_dict[i]['targets'] = find_targets_from_text(episode_dict[i]['text'])

    # find episode random events
    for i in episode_dict:
        for kw in ['table de hasard', 'tentez votre chance']:
            episode_dict[i][kw] = int(kw in episode_dict[i]['text'].lower())

    # find episode fights
    for i in episode_dict:
        episode_dict[i]['fight'] = find_fight_score_from_text(episode_dict[i]['text'])

    return episode_dict



def find_episode_markers_from_lines(lines):
    # episode_ids = [m.group(1).strip() for m in re.finditer('\n+\s*([0-9]+)\s*\n+', text)]
    # episode_ids = [
    #     (i, int(t.strip())) 
    #     for i, t in enumerate(text.split('\n')) 
    #     if t.strip().isdigit()
    # ]

    # episode_markers = [
    #     (i, int(p.strip()))
    #     for i, p in enumerate(paragraphs)
    #     if (not (' ' + ' '.join(paragraphs[:i]).strip())[-1].isalpha()
    #         or (' ' + ' '.join(paragraphs[:i]).strip())[-1] in ['.', '!', '?', ',']
    #     )
    #     and p.strip().isdigit()
    # ]
    # episode_idx, episode_ids = [list(m) for m in zip(*episode_markers)]

    # episode_markers = [
    #     (i, int(p.strip()))
    #     for i, p in enumerate(paragraphs)
    #     if ((' ' + ' '.join(paragraphs[:i]).strip())[-1] in ['.', '!', '?', ','])
    #     and p.strip().isdigit()
    # ]
    # episode_idx, episode_ids = [list(m) for m in zip(*episode_markers)]

    episode_markers = [
        (i, int(p.strip()))
        for i, p in enumerate(lines)
        if p.strip().isdigit()
    ]
    episode_markers = [
        mark for i, mark in enumerate(episode_markers)
        if all(j in [m[1] for m in episode_markers[:i]] for j in range(1, mark[1]))
    ]
    episode_max = max([m[1] for m in episode_markers])
    episode_markers = [
        mark for i, mark in enumerate(episode_markers)
        if all(j in [m[1] for m in episode_markers[i+1:]] for j in range(mark[1]+1, episode_max))
    ]
    return episode_markers



def find_targets_from_text(text):
    # find target ids, along with their span in the input text
    target_dict = {int(m.group(1)): {'span': m.span(1)} for m in re.finditer('au\s+([0-9]+)', text)}

    # find sentence chunk associated to each target id
    start_chars = [i.start() for i in re.finditer('\.', text)] + [t['span'][1] for t in target_dict.values()]
    for t in target_dict:
        span = target_dict[t]['span']
        start_idx = max([0] + [i+1 for i in start_chars if i < span[0]])
        sent = text[start_idx: span[1]].strip()
        target_dict[t]['sentence'] = sent
    return target_dict



def find_fight_score_from_text(text):
    scores = [
        # tuple(int(e) for e in m.groups())
        m.groups()
        for m in re.finditer('HABILETÉ[\s:;\.]+([0-9]+)\s+ENDURANCE[\s:;\.]+([0-9]+)', text)
    ]
    return (sum(int(sc[0]) for sc in scores), sum(int(sc[1]) for sc in scores))