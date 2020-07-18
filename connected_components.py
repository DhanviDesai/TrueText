import numpy as np
from swt import cal_swt
import cv2
import time
from pyrsistent import m
from get_image import read_image

def find_root(data_structure,node):
    if(data_structure[node] == node):
        return node
    else:
        node = find_root(data_structure,data_structure[node])
        return node

def union(data_structure,rank_data,first,second):
    first_root = find_root(data_structure,first)
    second_root = find_root(data_structure,second)

    first_rank = rank_data[first_root]
    second_rank = rank_data[second_root]

    if first_rank > second_rank:
        data_structure[second_root] = first_root
        rank_data[first_root] += 1
    elif first_rank < second_rank :
        data_structure[first_root] = second_root
        rank_data[second_root] += 1
    else:
        data_structure[second_root] = first_root
        rank_data[first_root] += 1

def get_dimensions(list_pixels):
    rect = cv2.minAreaRect(np.array([list_pixels]))
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    x = int(rect[0][0])
    y = int(rect[0][1])
    w = int(rect[1][0])
    h = int(rect[1][1])
    x = int(np.ceil(x))
    y = int(np.ceil(y))
    w = int(np.ceil(w))
    h = int(np.ceil(h))
    return x,y,w,h,box

def crop_img(img,width,height,box):
    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height-1],[0, 0],[width-1, 0],[width-1, height-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, M, (width, height))
    return warped


def get_words_list(filename):
    image_width,image_height,image,img_gray,v,canny,background_color = read_image(filename)
    # print(v)
    swt,sobelx,sobely = cal_swt(img_gray,canny,True)
    # print(swt.shape)
    draw = image.copy()
    data_structure = np.zeros(swt.shape,dtype='object')
    rank_data = np.zeros(swt.shape)
    for y in range(swt.shape[0]):
        for x in range(swt.shape[1]):
            data_structure[y,x] = (y,x)
    for y in range(swt.shape[0]):
        for x in range(swt.shape[1]):
            swt_point = swt[y,x]
            if(swt_point > 0 and swt_point < np.Infinity):
                neighbors = [(y,x+1),(y+1,x+1),(y+1,x)]
                for neighbor in neighbors:
                    try:
                        sw_n = swt[neighbor]
                        if(sw_n/swt_point < 3.0 or swt_point/sw_n < 3.0 ):
                            # print(neighbor)
                            union(data_structure,rank_data,(y,x),(neighbor))
                    except:
                        continue

    components = m()

    for y in range(swt.shape[0]):
        for x in range(swt.shape[1]):
            if(swt[y,x] > 0 and swt[y,x] < np.Infinity):
                comp = find_root(data_structure,(y,x))
                if(components.get(comp) is None):
                    components = components.set(comp,[(x,y)])
                else:
                    components.get(comp).append((x,y))

    # print('Number of goups ',len(components))


    for comp in components.keys():
        list_pixels = components.get(comp)
        if(len(list_pixels) < 2 ):
            components = components.remove(comp)
        var = np.var([swt[y,x] for x,y in list_pixels],ddof=1)
        if(var > v):
            if(components.get(comp) is not None):
                components = components.remove(comp)
        x,y,w,h,box = get_dimensions(list_pixels)
        if(np.ceil(h) < 12 or np.ceil(h) > 300):
            if(components.get(comp) is not None):
                components = components.remove(comp)
        try:
            if ( w/h > 10 or h/w > 10):
                if(components.get(comp) is not None):
                    components = components.remove(comp)
        except ZeroDivisionError :
            if components.get(comp) is not None:
                components = components.remove(comp)
        median = np.median([swt[y,x] for x,y in list_pixels])
        diameter = np.sqrt((w+10)**2 + (h+10)**2)
        if(diameter/v > 10):
            if(components.get(comp) is not None):
                components = components.remove(comp)

    # print('Final letter candidates ',len(components))

    total_h = 0
    total_w = 0
    total_num = 0
    for key in components.keys():
        list_pixels = components.get(key)
        x,y,w,h,box = get_dimensions(list_pixels)
        total_h += h
        total_w += w
        total_num += 1

    avg_h = np.ceil(total_h/total_num)
    avg_width = np.ceil(total_w/total_num)

    # print('avg_h',avg_h)
    # print('avg_width',avg_width)
    # print('size',2*(avg_h+avg_width))

    font_size = 2*(avg_h+avg_width)

    dtype = [('x',int),('y',int)]

    roots_list_words = np.array(list(components.keys()),dtype=dtype)

    sorted_list_words = np.sort(roots_list_words,order=['x','y'])

    #
    roots_lookup = m()

    data_structure_words = np.zeros(len(roots_list_words),dtype=np.int32)

    for i,key in enumerate(components.keys()):
        data_structure_words[i] = i
        roots_lookup = roots_lookup.set(key,i)

    # print('roots_lookup',roots_lookup)

    rank_data_words = np.zeros(len(data_structure_words),dtype=np.int32)

    for i in range(len(sorted_list_words) -1 ):
        comp1 = sorted_list_words[i]
        # print(comp1)
        comp1 = tuple((comp1[0],comp1[1]))
        comp2 = sorted_list_words[i+1]
        # print(comp2)
        comp2 = tuple((comp2[0],comp2[1]))
        list_pixels1 = components.get(comp1)
        list_pixels2 = components.get(comp2)
        cand1msw = np.mean([swt[y,x] for x,y in list_pixels1])
        cand2msw = np.mean([swt[y,x] for x,y in list_pixels2])
        x1,y1,w1,h1,box1 = get_dimensions(list_pixels1)
        # x1 = x1 - w1//2
        # y1 = y1 - h1//2
        x2,y2,w2,h2,box2 = get_dimensions(list_pixels2)
        # x2 = x2 - w2//2
        # y2 = y2 - h2//2
        if(w1>w2):
            max_w = w1
        else:
            max_w = w2
        if(h1>h2):
            max_h = h1
        else:
            max_h=h2
        # if(cand1msw/cand2msw > 2 or cand2msw/cand1msw > 2):
        #     continue
        # if(h1/h2 > 2 or h2/h1 > 2):
        #     continue
        # if(abs(x1- x2 ) > 3*max_w):
        #     continue
        if(abs(y1-y2) > (h1+h2)/2 ):
            continue
        # print('Joined the two')
        union(data_structure_words,rank_data_words,roots_lookup.get(comp1),roots_lookup.get(comp2))
    #
    # print('data_structure_words',data_structure_words)

    # print('rank_data_words',rank_data_words)
    #
    words_list = m()

    for key in components.keys():
        # print(key)
        index = roots_lookup.get(key)
        # print(index)
        # print(data_structure_words[index])
        element_root = find_root(data_structure_words,int(data_structure_words[index]))
        # print(element_root)
        if(words_list.get(element_root) is None):
            words_list = words_list.set(element_root,[])
        this_list = components.get(key)
        root_list = words_list.get(element_root)
        append_list = root_list + this_list
        words_list = words_list.set(element_root,append_list)

        # print(words_list)

    return image_width,image_height,words_list,draw,background_color,avg_h,avg_width

    # cv2.imwrite('draw'+filename,draw)
    # end = time.time()
