# -*- coding: utf-8 -*-

# import sys 
# import os


#sys.path.insert(0, os.path.join(sys.path[0], '../..')) #add parents-parent directory to path
#sys.path.insert(0,'../../')

import json
#import glob
import numpy as np
from ocrp import trp

#https://github.com/aws-samples/textract-paragraph-identification/blob/main/lambda_helper.py

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
            
            # line_width_after = round((next_line_info['right_indent'] - current_line_info['right_indent']), 2)
            # width_with_prev = round((current_line_info['right_indent'] - previous_line_info['right_indent']), 2)
            # current_line_info.update(line_width_before=width_with_prev)
            # current_line_info.update(line_width_after=line_width_after)
            
            text_info_with_line_spacing_info.append(current_line_info)
        else:
            text_info_with_line_spacing_info.append(None)
        i += 1
    return text_info_with_line_spacing_info



def get_bounding_boxes(document):
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
    for i, page in enumerate(document.pages):
        #per_page_text = []
        for line in page.lines:
            block_text_dict = {}
            running_sequence_number += 1
            block_text_dict.update(text=line.text)
            block_text_dict.update(page=i)
            block_text_dict.update(bbox=[round(line.geometry.boundingBox.left, 3),
                                         round(line.geometry.boundingBox.top, 3),
                                         round(line.geometry.boundingBox.width, 3),
                                         round(line.geometry.boundingBox.height, 3)])
            
            font_height = round(line.geometry.boundingBox.height, 3)
            line_number = running_sequence_number
            block_text_dict.update(font_height=round(line.geometry.boundingBox.height, 3))
            block_text_dict.update(indent_from_top=round(line.geometry.boundingBox.top, 3))
            block_text_dict.update(text_width=round(line.geometry.boundingBox.width, 3))
        

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
    
def display(document):
    #if display==True:
    from PIL import Image, ImageDraw, ImageFont
    mode= 'RGB' # for colorimage"L" (luminance)forgreyscaleimages,"RGB"for truecolorimages,and "CMYK"forpre-pressimages.
    image= None 
    #setimagesizeto A4
    width= 2480
    height= 3508
    size= (width,height) #w,h@300ppi    I
    color= (255,255,255) 
    # specifiedfontsize 
    font= ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 24)
    
    
    for page in range(0,len(document.pages)): 
        image= Image.new(mode, size, color)
        draw= ImageDraw.Draw(image)
        
        for block in document.pageBlocks[3]['Blocks']:
        #for block in document.pageBlocks[page]['Blocks']:
            if block['BlockType'] == "LINE":
                points=[]
                for polygon in block['Geometry']['Polygon']: 
                    points.append((width * polygon['X'], height * polygon['Y']))
                draw.polygon((points),outline='black')
                left=block['Geometry']['BoundingBox']['Left']*width
                top=block['Geometry']['BoundingBox']['Top']*height
                
                # left=points[0][0]
                # top=points[0][1]
                draw.text((left,top), fill="black", text=block['Text'] , font=font)
        image.show()
        
    lines = 0
    for page in range(0,len(document.pages)): 
        for block in document.pageBlocks[page]['Blocks']:
            if block['BlockType'] == "LINE":
                lines+= 1

def display_boundingBox(boxes_merged):
    #if display==True:
    from PIL import Image, ImageDraw, ImageFont
    mode= 'RGB' # for colorimage"L" (luminance)forgreyscaleimages,"RGB"for truecolorimages,and "CMYK"forpre-pressimages.
    image= None 
    #setimagesizeto A4
    width= 2480
    height= 3508
    size= (width,height) #w,h@300ppi    I
    color= (255,255,255) 
    # specifiedfontsize 
    font= ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 24)
    
    
    #for page in range(0,len(document.pages)): 
    image= Image.new(mode, size, color)
    draw= ImageDraw.Draw(image)
    
    for i, box in enumerate(boxes_merged):
        x, y, w, h = box
        #print([(int(x*width), int(y*height)), (int(w*width), int(h*height))])
        draw.rectangle([(int(x*width), int(y*height)), (int(x*width)+int(w*width), int(y*height)+int(h*height))], fill="white", outline='black')
        left = int(x*width)
        top = int(y*height)
        draw.text((left,top), fill="black", text=str(i) , font=font)
    image.show()

        
def get_lines_in_boundingBox(document, page_idx, paragraph_box):
    #logging.info('finding features... ')

    # Coordinates are from top-left corner [0,0] to bottom-right [1,1]
    x, y, w, h = paragraph_box
    bbox = trp.BoundingBox(width=w+0.002, height=h+0.002, left=x-0.001, top=y-0.001)
    lines =  document.pages[page_idx].getLinesInBoundingBox(bbox)
         
    # # Print only the lines contained in the Bounding Box
    # for line in lines:
    #     print(line.text)

    block_dict = {'para':[],'text':[], 'ids':[], 'boundingBox':paragraph_box}
    for line in lines:
        #for word in    e.words:
        block_dict['text'].append(line.text.lower())
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
                
if __name__ == "__main__":
    
    
    filen = '/Users/ross/Mirror/GitHub/src/ResLife/data/processed/textract/07316B_insurance_product_disclosure_statement.json'
    #filen = '/Users/ross/Mirror/GitHub/src/ResLife/data/processed/textract/poc/PD01313_9268_Your_Upgrade_Final_PD01313.json'
    #filen = '/Users/ross/Mirror/GitHub/src/ResLife/data/processed/textract/poc/PD00759_Income_Insurance_Plan_Reviewable_Indemnity_BY__CY__DY.json'
    #filen = fname
    with open(filen,'rt') as handle:
        doc =  json.load(handle)
        if 'ExtractedText' in doc.keys():
            document = trp.Document(doc['ExtractedText'])
        else:
            document = trp.Document(doc)
            
    # total_text_with_info, font_sizes_and_line_numbers = get_the_text_with_required_info(document)
    
    # data = get_text_with_line_spacing_info(total_text_with_info)
    
    #paras = extract_paragraphs_only(data)
    
    
    total_text_with_info, font_sizes_and_line_numbers = get_bounding_boxes(document)
    all_pages = []
    
    for i, page in enumerate(document.pages):
        rec = [x['bbox'] for x in total_text_with_info if x['page']==i]
        display_boundingBox(rec)
        #bbox_groups = utils.group_rectangles_proximity(rec, dist_x=0, dist_y=0.007)
        bbox_groups = group_boundingBox_by_proximity(rec, dist_x=0, dist_y=0.007)
        display_boundingBox(bbox_groups)
        
        paras = []
        for box in bbox_groups:
            print(box)
            page = 4
            paras.append(get_lines_in_boundingBox(document, i, box))
        
        #paragraph =[]
        for i, para in enumerate(paras):
            #paragraph = get_lines_in_boundingBox(document, i, paragraph_box)
            #text = paragraph.para
            all_pages.append({'pdf':filen.split('/')[-1][:-5],'page':i, 'paragraph':i, 'para': para['para'], 'boundingBox':para['boundingBox']})
    # paragraph_box = bbox_groups[0]
    
    # lines = getLinesInBoundingBox(document, paragraph_box)
    





