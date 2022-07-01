import os
import sys
from io import open, BytesIO
import re

# data
import numpy as np

# pdf
import fitz # name of pymupdf





#**********************************************************
#*                       content                          *
#**********************************************************

def parse_pdf_raw_text(file_path):
    doc = fitz.open(file_path)
    text = [page.get_text('text') for page in doc]
    text = ''.join(text)
    return text



def get_reordered_text(span, line_dir):
    chars = list(span['chars'])
    chars.sort(key = lambda c: float(c['bbox'][0])*line_dir) #origin
    text = ''.join([c['c'] for c in chars])
    return text



def parse_page_df_text(page, precision = 4):
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



def parse_df_text(doc, precision = 4):
    doc_text = []
    # iterate over pages
    # list of methods for Page objects
    # see the docs: https://pymupdf.readthedocs.io/en/latest/page.html
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





