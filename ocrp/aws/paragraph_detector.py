# -*- coding: utf-8 -*-

# import sys 
# import os


#sys.path.insert(0, os.path.join(sys.path[0], '../..')) #add parents-parent directory to path
#sys.path.insert(0,'../../')

import json
import numpy as np
#import format_helper


#https://github.com/aws-samples/textract-paragraph-identification/blob/main/lambda_helper.py

class BoundingBox:
    def __init__(self, width, height, left, top):
        self._width = width
        self._height = height
        self._left = left
        self._top = top

    def __str__(self):
        return "width: {}, height: {}, left: {}, top: {}".format(self._width, self._height, self._left, self._top)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._left + self._width

    @property
    def top(self):
        return self._top

    @property
    def bottom(self):
        return self._top + self._height
    
def get_headers_and_their_line_numbers(required_mapping, total_text_with_info):
    header_and_its_line_numbers = {}
    for header in required_mapping.keys():
        for each_line in total_text_with_info:
            if each_line['font_height'] == header:
                header_and_its_line_numbers[each_line['text']] = {'line_num':each_line['line_number'],'page':each_line['page']}
    return header_and_its_line_numbers


def get_headers_and_paragraphs(header_and_its_line_numbers,
                               total_text_with_info):
    headers_to_paragraphs = {}
    header_list_iterator = iter(header_and_its_line_numbers)
    header = next(header_list_iterator, None)

    while header:
        header_line_number = header_and_its_line_numbers[header]['line_num']
        current_header = header
        header = next(header_list_iterator, None)
        paragraph_data = []
        if header:
            next_header_line_number = header_and_its_line_numbers[header]['line_num']
            for each_line in total_text_with_info:
                if (each_line['line_number'] > header_line_number) and (
                        each_line['line_number'] < next_header_line_number):
                    paragraph_data.append(each_line['text'])
        else:
            for each_line in total_text_with_info:
                if each_line['line_number'] > header_line_number:
                    paragraph_data.append(each_line['text'])

        headers_to_paragraphs[current_header] = " ".join(paragraph_data)
    return headers_to_paragraphs
    
def get_the_text_with_required_info(document):
    total_text = []
    total_text_with_info = []
    running_sequence_number = 0

    font_sizes_and_line_numbers = {}
    for i, page in enumerate(document.pages):
        #per_page_text = []
        for line in page.lines:
            block_text_dict = {}
            running_sequence_number += 1
            block_text_dict.update(text=line.text)
            block_text_dict.update(page=i)
            block_text_dict.update(left_indent=round(line.geometry.boundingBox.left, 2))
            font_height = round(line.geometry.boundingBox.height, 2)
            line_number = running_sequence_number
            block_text_dict.update(font_height=round(line.geometry.boundingBox.height, 2))
            block_text_dict.update(indent_from_top=round(line.geometry.boundingBox.top, 2))
            block_text_dict.update(text_width=round(line.geometry.boundingBox.width, 2))
            block_text_dict.update(right_indent=round(block_text_dict['left_indent']+block_text_dict['text_width'], 2))

            block_text_dict.update(line_number=running_sequence_number)


            if font_height in font_sizes_and_line_numbers:
                line_numbers = font_sizes_and_line_numbers[font_height]
                line_numbers.append(line_number)
                font_sizes_and_line_numbers[font_height] = line_numbers
            else:
                line_numbers = []
                line_numbers.append(line_number)
                font_sizes_and_line_numbers[font_height] = line_numbers

            total_text.append(line.text)
            #per_page_text.append(line.text)
            total_text_with_info.append(block_text_dict)

    return total_text_with_info, font_sizes_and_line_numbers

#https://github.com/aws-samples/textract-paragraph-identification/blob/main/lambda_helper.py
def get_text_with_line_spacing_info(total_text_with_info):
    i = 1
    text_info_with_line_spacing_info = []
    while (i < len(total_text_with_info) - 1):
        previous_line_info = total_text_with_info[i - 1]
        current_line_info = total_text_with_info[i]
        next_line_info = total_text_with_info[i + 1]
        if current_line_info['page'] == next_line_info['page'] and previous_line_info['page'] == current_line_info[
            'page']:
            line_spacing_after = round((next_line_info['indent_from_top'] - current_line_info['indent_from_top']), 2)
            spacing_with_prev = round((current_line_info['indent_from_top'] - previous_line_info['indent_from_top']), 2)
            current_line_info.update(line_space_before=spacing_with_prev)
            current_line_info.update(line_space_after=line_spacing_after)

            
            text_info_with_line_spacing_info.append(current_line_info)
        else:
            text_info_with_line_spacing_info.append(None)
        i += 1
    return text_info_with_line_spacing_info



def get_bounding_boxes(page):
    """
    get the bounding boxes for lines in the form [x,y,w,h]
    where x,y,w and h are in fractional page coordinates. 
    can convert to pixels by multiplying by width and height in pixels

    Parameters
    ----------
    document : TYPE
        DESCRIPTION.

    Returns
    -------
    total_text_with_info : TYPE
        DESCRIPTION.
    font_sizes_and_line_numbers : TYPE
        DESCRIPTION.

    """
    total_text = []
    total_text_with_info = []
    running_sequence_number = 0

    font_sizes_and_line_numbers = {}
    font_sizes_and_line_ids = {}
    #for i, page in enumerate(document.pages):
        #per_page_text = []
    for line in page.lines:
        block_text_dict = {}
        running_sequence_number += 1
        block_text_dict.update(text=line.text)
        block_text_dict.update(line_id=line.id)
        #block_text_dict.update(page=i)
        block_text_dict.update(bbox=[round(line.geometry.boundingBox.left, 3),
                                     round(line.geometry.boundingBox.top, 3),
                                     round(line.geometry.boundingBox.width, 3),
                                     round(line.geometry.boundingBox.height, 3)])
        
        font_height = round(line.geometry.boundingBox.height, 3)
        line_number = running_sequence_number
        line_id = line.id
        block_text_dict.update(font_height=round(line.geometry.boundingBox.height, 3))
        block_text_dict.update(indent_from_top=round(line.geometry.boundingBox.top, 3))
        block_text_dict.update(text_width=round(line.geometry.boundingBox.width, 3))
        block_text_dict.update(indent_from_left=round(line.geometry.boundingBox.left, 3))
    

        block_text_dict.update(line_number=running_sequence_number)


        if font_height in font_sizes_and_line_numbers:
            line_numbers = font_sizes_and_line_numbers[font_height]
            line_numbers.append(line_number)
            font_sizes_and_line_numbers[font_height] = line_numbers
        else:
            line_numbers = []
            line_numbers.append(line_number)
            font_sizes_and_line_numbers[font_height] = line_numbers

        if font_height in font_sizes_and_line_ids:
            line_ids = font_sizes_and_line_ids[font_height]
            line_ids.append(line_id)
            font_sizes_and_line_numbers[font_height] = line_ids
        else:
            line_ids = []
            line_numbers.append(line_id)
            font_sizes_and_line_numbers[font_height] = line_ids

        total_text.append(line.text)
        #per_page_text.append(line.text)
        total_text_with_info.append(block_text_dict)

    return total_text_with_info, font_sizes_and_line_numbers, font_sizes_and_line_ids


def get_paragraphs_based_on_period(data):
    paragraph_data = []
    paras = []
    i = 0
    while i < len(data):
        line = data[i]
        if line:
            if line['text'][-1] == '.':
                paragraph_data.append(line['text'])
                paras.append(' '.join(paragraph_data))
                paragraph_data = []
            else:
                paragraph_data.append(line['text'])
        i += 1
    return paras

def get_headers_to_child_mapping(font_sizes_and_line_numbers):
    unique_font_heights = []
    for font_height in font_sizes_and_line_numbers.keys():
        lines_with_same_font = font_sizes_and_line_numbers[font_height]
        if len(lines_with_same_font) > 1:
            unique_font_heights.append(font_height)

    fonts_for_headers = list(set(unique_font_heights))
    i = 0
    headers_and_its_child = {}
    while i + 1 < len(fonts_for_headers):
        headers_and_its_child[fonts_for_headers[i]] = fonts_for_headers[i + 1]
        i += 1
    return headers_and_its_child
    
def display_text(page, canvas):

    
    for block in page.blocks:
    #for block in document.pageBlocks[page]['Blocks']:
        if block['BlockType'] == "LINE":
            # points=[]
            # for polygon in block['Geometry']['Polygon']: 
            #     points.append((width * polygon['X'], height * polygon['Y']))
            # draw.polygon((points),outline='black')
            left=block['Geometry']['BoundingBox']['Left']*canvas['width']
            top=block['Geometry']['BoundingBox']['Top']*canvas['height']
            
            # left=points[0][0]
            # top=points[0][1]
            canvas['draw'].text((left,top), fill="black", text=block['Text'] , font=canvas['font'])

    
    return canvas


def display_boundingBox(boxes_merged, canvas):

    
    for i, box in enumerate(boxes_merged):
        x, y, w, h = box
        #print([(int(x*width), int(y*height)), (int(w*width), int(h*height))])
        canvas['draw'].rectangle([(int(x*canvas['width']), int(y*canvas['height'])), (int(x*canvas['width'])+int(w*canvas['width']), int(y*canvas['height'])+int(h*canvas['height']))], fill=None, outline='black')
        # left = int(x*canvas['width'])
        # top = int(y*canvas['height'])
        #canvas['draw'].text((left,top), fill="black", text=str(i) , font=canvas['font'])
        

    return canvas

def create_canvas():
    from PIL import Image, ImageDraw, ImageFont
    mode= 'RGB' # for colorimage"L" (luminance)forgreyscaleimages,"RGB"for truecolorimages,and "CMYK"forpre-pressimages.
    image= None 
    #set image size to A4
    width= 2480
    height= 3508
    size= (width,height) #w,h@300ppi    I
    color= (255,255,255) 
    # specified font size 
    font= ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 24)
    
    
    #for page in range(0,len(document.pages)): 
    image= Image.new(mode, size, color)
    draw= ImageDraw.Draw(image)
    
    return {'image':image, 'draw':draw, 'width':width, 'height':height, 'font':font}
 
        
def get_lines_in_boundingBox(page, paragraph_box):
    #logging.info('finding features... ')

    # Coordinates are from top-left corner [0,0] to bottom-right [1,1]
    x, y, w, h = paragraph_box
    bbox = BoundingBox(width=w+0.002, height=h+0.002, left=x-0.001, top=y-0.001)
    #lines =  document.pages[page_idx].getLinesInBoundingBox(paragraph_box)
    lines =  page.getLinesInBoundingBox(bbox)
         


    block_dict = {'para':[],'text':[], 'ids':[], 'boundingBox':paragraph_box}
    for line in lines:
        #for word in    e.words:
        block_dict['text'].append(line.text + '\n')
        block_dict['ids'].append(line.id)
        #print(line.text.lower())
        
        
    block_dict['para'].append(' '.join(block_dict['text']))
    

    return block_dict


def _union(a,b):  #returns the union of two boxes
    x = min(a[0], b[0])
    y = min(a[1], b[1])
    w = max(a[0]+a[2], b[0]+b[2]) - x
    h = max(a[1]+a[3], b[1]+b[3]) - y
    return [x, y, w, h]

def _intersect(a,b, dist_x=20, dist_y=5):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    w = min(a[0]+a[2], b[0]+b[2]) - x + dist_x #20
    h = min(a[1]+a[3], b[1]+b[3]) - y + dist_y
    if w<0 or h<0:                                              # in original code :  if w<0 or h<0:
        return False
    return True


def group_boundingBox_by_proximity(rec, dist_x=20, dist_y=0):
    """
    Union of intersecting rectangles based on proximity.
    Args:
        rec - list of rectangles in form [x, y, w, h]
    Return:
        list of grouped ractangles 
    """
    tested = [False for i in range(len(rec))]
    final = []
    i = 0
    while i < len(rec):
        if not tested[i]:
            j = i+1
            while j < len(rec):
                if not tested[j] and _intersect(rec[i], rec[j], dist_x, dist_y):
                    rec[i] = _union(rec[i], rec[j])
                    tested[j] = True
                    j = i
                j += 1
            final += [rec[i]]
        i += 1
    
    return np.asarray(final)

def extract_paragraphs(filen, page, dist_x=0, dist_y = 0.007, display=False):

    canvas = None
    all_parapraphs = []
    if display==True:
        canvas = create_canvas()
        canvas = display_text(page, canvas)
        canvas['image'].show()

    total_text_with_info, font_sizes_and_line_numbers = get_bounding_boxes(page)

    rec = [x['bbox'] for x in total_text_with_info ]
    if display==True:
        canvas = display_boundingBox(rec, canvas)
        canvas['image'].show()
        
    bbox_groups = group_boundingBox_by_proximity(rec, dist_x=dist_x, dist_y=dist_y)
    if display==True:
        #display(page)
        canvas =  display_boundingBox(bbox_groups, canvas)
        canvas['image'].show()

    paras = []
    for box in bbox_groups:
        # x, y, w, h = box
        # bbox = BoundingBox(width=w+0.002, height=h+0.002, left=x-0.001, top=y-0.001)
        paras.append(get_lines_in_boundingBox(page, box))

    pageBlock = page.blocks[0]
    page_num = pageBlock['Page']-1
    for j, para in enumerate(paras):
        all_parapraphs.append({'pdf':filen.split('/')[-1][:-5],'page':page_num, 'paragraph':j,'text': ' '.join(para['para']), 'boundingBox':para['boundingBox']})
            
    return all_parapraphs

   
                
if __name__ == "__main__":
    
    filen = '.json'
        
    
    import trp
    import pandas as pd
    
    with open(filen,'rt') as handle:
        doc =  json.load(handle)
        if 'ExtractedText' in doc.keys():
            document = trp.Document(doc['ExtractedText'])
        else:
            document = trp.Document(doc)
    
    
    page = document.pages[123]
    df = pd.DataFrame(extract_paragraphs(filen, page, dist_x=0, dist_y = 0.007, display=True))
    pg = df[df['page']==123]
    para = pg[pg['paragraph']==4]
    print(para['text'].iloc[0])
    




