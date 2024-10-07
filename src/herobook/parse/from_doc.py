from typing import Dict, Any
import copy
import pandas as pd


def parse_episodes_from_doc(doc) -> Dict[int, Dict[str, str]]:
    '''
    Convert a herobook doc into a dict of episodes.
    '''
    raise NotImplementedError


def parse_pdf_df_text(doc, precision = 4):
    '''
    Experimental.
    Parse content of multiple pages as a table of text blocks with metadata.
    '''
    doc_text = []
    for page_idx, page in enumerate(doc):
        page_text = parse_page_df_text(page, precision)
        doc_text += [[page_idx] + el for el in page_text]

    df_text = pd.DataFrame(doc_text, columns = [
        'Page', 'Block', 'Line', 'Span',
        'Text', 'Text_reordered', 'Font', 'Fontsize',
        'Block_x_left', 'Block_y_top', 'Block_x_right', 'Block_y_bottom',
        'Block_x_left_ratio', 'Block_y_top_ratio', 'Block_x_right_ratio', 'Block_y_bottom_ratio',
        'Line_x_left', 'Line_y_top', 'Line_x_right', 'Line_y_bottom',
        'Line_x_left_ratio', 'Line_y_top_ratio', 'Line_x_right_ratio', 'Line_y_bottom_ratio',
        'Span_x_left', 'Span_y_top', 'Span_x_right', 'Span_y_bottom',
        'Span_x_left_ratio', 'Span_y_top_ratio', 'Span_x_right_ratio', 'Span_y_bottom_ratio',
    ]) 
    df_text['Block_y_top_ratio']    += df_text.Page
    df_text['Block_y_bottom_ratio'] += df_text.Page
    df_text['Line_y_top_ratio']     += df_text.Page
    df_text['Line_y_bottom_ratio']  += df_text.Page
    df_text['Span_y_top_ratio']     += df_text.Page
    df_text['Span_y_bottom_ratio']  += df_text.Page
    df_text['Center_x_ratio'] = (df_text.Span_x_right_ratio + df_text.Span_x_left_ratio)/2
    df_text['Center_y_ratio'] = (df_text.Span_y_bottom_ratio + df_text.Span_y_top_ratio)/2
    return df_text


def parse_page_df_text(page, precision = 4):
    '''
    Experimental.
    Parse content of a page as a table of text blocks with metadata.
    '''
    page_text = []
    
    # coordinates of lower right corner
    page_x, page_y = page.rect[-2:]
    rect = [page_x, page_y, page_x, page_y]
        
    # get content and position of texts
    textpage = page.get_textpage()      # convert Page to TextPage object
    content = textpage.extractRAWDICT() # get page content as dict
    # equivalently :
    #content = page.get_text(('rawdict'))
    # alternatively :
    #content = textpage.extractDICT()   # get page content as dict
    # equivalently :
    #content = page.get_text(('dict'))

    # blocks aren't sorted by top-to-bottom order !!
    #  lines aren't sorted by top-to-bottom order !!

    blocks = list(content['blocks'])
    blocks = [b for b in blocks if 'lines' in b]
    blocks.sort(key = lambda b: (
        min([float(span['bbox'][1]) for l in b['lines'] for span in l['spans']]), # from top to bottom
        min([float(span['bbox'][0]) for l in b['lines'] for span in l['spans']])  # from left to right
    ))
    for block_idx, block in enumerate(blocks):
        block_x0, block_y0, block_x1, block_y1 = block['bbox']
        block_x0_ratio, block_y0_ratio, block_x1_ratio, block_y1_ratio = [round(v/w, precision) for v, w in zip(block['bbox'], rect)]
        lines = list(block['lines'])
        lines.sort(key = lambda l: (
            min([float(span['bbox'][1]) for span in l['spans']]), # from top to bottom
            min([float(span['bbox'][0]) for span in l['spans']])  # from left to right
        ))
        for line_idx, line in enumerate(lines):
            line_x0, line_y0, line_x1, line_y1 = line['bbox']
            line_x0_ratio, line_y0_ratio, line_x1_ratio, line_y1_ratio = [round(v/w, precision) for v, w in zip(line['bbox'], rect)]
            spans = line['spans']

            for span_idx, span in enumerate(spans):
                span_x0, span_y0, span_x1, span_y1 = span['bbox']
                span_x0_ratio, span_y0_ratio, span_x1_ratio, span_y1_ratio = [round(v/w, precision) for v, w in zip(span['bbox'], rect)]
                text = ''.join([c['c'] for c in span['chars']])
                text_reordered = get_reordered_text(span, line['dir'][0])
                font = span['font']
                size = span['size']

                page_text.append([
                    block_idx, line_idx, span_idx,
                    text, text_reordered, font, size,
                    block_x0, block_y0, block_x1, block_y1,
                    block_x0_ratio, block_y0_ratio, block_x1_ratio, block_y1_ratio,
                    line_x0, line_y0, line_x1, line_y1,
                    line_x0_ratio, line_y0_ratio, line_x1_ratio, line_y1_ratio,
                    span_x0, span_y0, span_x1, span_y1,
                    span_x0_ratio, span_y0_ratio, span_x1_ratio, span_y1_ratio,
                ])
    return page_text


def get_reordered_text(span: Dict[str, Any], line_dir):
    chars = list(span['chars'])
    chars.sort(key = lambda c: float(c['bbox'][0])*line_dir)
    text = ''.join([c['c'] for c in chars])
    return text


def find_df_episode_markers(df_text):
    df_text = copy.deepcopy(df_text)
    
    line_y_top = df_text.Line_y_top_ratio.tolist()
    line_y_bottom = df_text.Line_y_bottom_ratio.tolist()

    df_text['Line_upper_delta_ratio'] = [a-b for a, b in zip(line_y_top, [0] + line_y_bottom[:-1])]
    df_text['Line_lower_delta_ratio'] = [a-b for a, b in zip(line_y_top[1:] + [line_y_top[-1]], line_y_bottom)]
    
    # define episode ids as "digits, that are significantly separated form other spans on the y-axis"
    df_episode_ids = df_text[(
        (df_text.Text.apply(lambda t: t.strip().isdigit())) & # digit
        (df_text.Line_upper_delta_ratio > 0.01) &             # significantly separated from previous span (>1% of page height)
        (df_text.Line_lower_delta_ratio > 0.01)               # significantly separated from next span (>1% of page height)
    )] 
    episode_ids_row_idx = df_episode_ids.index.tolist()
    df_episode_ids = df_text.iloc[episode_ids_row_idx]
    return df_episode_ids


def parse_hyperlinks(doc):
    links = []
    x = 10
    # for each page, get hyperlinks with :
    # - source page number
    # - target page number
    # - source bounding box coordinates
    # - target point coordinates
    for page_idx, page in enumerate(doc):
        page_links = page.get_links()
        page_links = [
            [page_idx] + list(link['from']) + [link['page']] + list(link['to']) + [page.get_textbox(link["from"] + (-x, -x, x, x))]
            for link in page_links
            if ('page' in link and 'from' in link and 'to' in link)
        ]
        links += page_links
    df_links = pd.DataFrame(links, columns = [
        'Source_page', 'Source_x_left', 'Source_y_top',  'Source_x_right', 'Source_y_bottom',  
        'Target_page', 'Target_x', 'Target_y',
        'Text',
    ])
    return df_links


def find_source_ids(df_links, df_episode_ids):
    def find_source(link, df_episode_ids):
        df = df_episode_ids
        df = df[(df.Page < link.Source_page) | (
                (df.Page == link.Source_page) & 
                (df.Span_y_bottom <= link.Source_y_top)
            )]
        target = df.Text.tolist()[-1]
        return target
    
    return df_links.apply(
        func = lambda link: find_source(link, df_episode_ids),
        axis = 1,
    )


def find_target_ids(df_links, df_episode_ids):
    def find_target(link, df_episode_ids):
        df = df_episode_ids
        df = df[(df.Page > link.Target_page) | (
                (df.Page == link.Target_page) & 
                (df.Span_y_bottom >= link.Target_y)
            )]
        target = df.Text.tolist()[0]
        return target
    
    return df_links.apply(
        func = lambda link: find_target(link, df_episode_ids),
        axis = 1,
    )