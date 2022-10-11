from django.http import request
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import mss
import cv2 as cv
# import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import pygetwindow as gw
from googletrans import Translator
import re
from deep_translator import GoogleTranslator
import textwrap
import time
from PIL import ImageGrab
import random
import base64
# import win32gui
# import win32ui
# import win32con
frame = []


def home(request):
    list_of_openwindows = gw.getAllTitles()
    context = {
        # list_of_openwindows: 'list_of_openwindows'
    }
    print(list_of_openwindows)
    return render(request, 'home.html', context)

def getImage(request):
    _, img = cv2.imencode('.jpg',cv2.imread(frame))
    img = base64.b64encode(img)
    return JsonResponse({'image': img.decode('ascii')}) # a json containing base64 string of image is returne

def viewImage(request):
    return render(request, 'getImage.html')


def run(request):
    with mss.mss() as sct:
        loop_time = time.time()
        while(True):
            window = gw.getWindowsWithTitle('Document1 - Word')[0]
            x = window.left 
            y = window.top + 120
            w = window.width
            h = window.height - 140
            monitor = {"top": y, "left": x, "width": w, "height": h}
            frame = np.array(sct.grab(monitor))
            #frame2 = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
            
            results = pytesseract.image_to_data(frame, output_type=Output.DICT, config = 'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890$')

            # we will be putting words in sentences according to blocks
            block_dict = {'left': [], 'top': [], 'width': [], 'height': [], 'text': [], 'block_num': []}
            blocks_text = []

            block_id  = results["block_num"][0]
            tot_text = ""

            n = len(results["text"])
            temp_elem = ""

            k = 0
            flag = 0 # check for first time

            for i in range(0, n):

                block = results["block_num"][i]
                elem = results["text"][i]
                conf = float(results["conf"][i])
                x = results["left"][i]
                y = results["top"][i]
                w = results["width"][i]
                h = results["height"][i]
                is_comp = results["level"][i]

                if(conf>=40 and is_comp == 5):
                    elem = "".join([c if ord(c) < 128 else "" for c in elem]).strip()
                    elem = re.sub(r'[^.,()?;0-9a-zA-Z*]', '', elem)
                    #elem = elem.replace("\n", " ")
                    elem = elem.replace("*,","")

                    if(len(elem) == 0):
                        continue

                    block_dict["text"].append(elem)
                    block_dict["left"].append(results["left"][i])
                    block_dict["top"].append(results["top"][i])
                    block_dict["width"].append(results["width"][i])
                    block_dict["height"].append(results["height"][i])
                    block_dict["block_num"].append(results["block_num"][i])

            indexes = [block_dict["block_num"].index(x) for x in set(block_dict["block_num"])]
            n = len(block_dict['text'])
            indexes.append(n)
            indexes.sort()
            indexes.pop(0)

            k = 0
            temp = ''
            tot_text = '' 
            fin_dict = {'left': [], 'top': [], 'width': [], 'height': [], 'text': []}
            for i in indexes:

                x = block_dict['left'][k]
                y = block_dict['top'][k]
                w = block_dict['width'][k]
                h = block_dict['height'][k]

                for j in range(k, i):
                    temp_text = block_dict['text'][j]
                    temp_x = block_dict['left'][j]
                    temp_y = block_dict['top'][j]
                    temp_w = block_dict['width'][j]
                    temp_h = block_dict['height'][j]

                    tot_text = tot_text + ' ' + temp_text

                    if(temp_x < x):
                        x = temp_x
                    if(temp_y < y):
                        y = temp_y
                    if((temp_w + temp_x) > w):
                        w = temp_w + temp_x
                    if((temp_h + temp_y) > h):
                        h = temp_h + temp_y

                fin_dict['text'].append(tot_text)
                fin_dict['left'].append(x)
                fin_dict['top'].append(y)
                fin_dict['width'].append(w)
                fin_dict['height'].append(h)

                tot_text = ''
                k = i

            #print(block_dict)
            #frame = window_capture('The Myth Of Sisyphus.pdf - WPS Office')
            
            translated = []
            for i in fin_dict["text"]:
                translated.append(GoogleTranslator(source='auto', target='en').translate(i))
            
            n = len(fin_dict['text'])
            for i in range(0, n):

                #elem = fin_dict["text"][i]
                elem = translated[i]
                x = fin_dict["left"][i]
                y = fin_dict["top"][i]
                w = fin_dict["width"][i]
                h = fin_dict["height"][i]

                y_temp = y
    #             print(w)
    #             print(x)
    #             print(elem)
                if((w-x) <= 7.5):
                    continue
                    
                wrapped_text = textwrap.wrap(elem, width = int((w-x)/7.5))
                cv.rectangle(frame, (x, y), (w, h), (255, 255, 255), -1)

                for j, line in enumerate(wrapped_text):
                    textsize = cv.getTextSize(line, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]

                    gap = textsize[1] + 5

                    y_temp = int((y + textsize[1]) ) + (j) * gap
                    #y_temp = y + gap * j
                    #x = int((x - textsize[0]) )

                    cv.putText(frame, line, (x, y_temp ), cv.FONT_HERSHEY_SIMPLEX,
                                0.5, 
                                (0,0,255), 
                                1, 
                                lineType = cv.LINE_AA)
                    #cv.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), -1)
                    #cv.putText(frame, elem, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX,
            #     print(elem, " ", x, " ", y)
            #     cv.putText(frame, elem, (x, y + 10), cv.FONT_HERSHEY_SIMPLEX,
                        #0.5, (0, 0, 255), 1)
            cv.imshow('output', frame)
            print("FPS ", (1 /(time.time() - loop_time)))
            loop_time = time.time()
            if(cv.waitKey(1) & 0xFF == ord('q')):
                cv.destroyAllWindows()
                break
        
    return HttpResponse("<h1> fgfgf</h1>")