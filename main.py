from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import pink, green, brown, white,black
from reportlab.lib.pagesizes import A4
import pytesseract
import cv2

from connected_components import get_words_list,get_dimensions,crop_img

filename = "C:\\Users\\Dhanvi\\Understand_Image\\Test1.png"
image_width,image_height,words_list,draw,background_color,avg_h,avg_width = get_words_list(filename)
# print(len(words_list))
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\Tesseract-OCR\\tesseract.exe'
c = Canvas('Trial.pdf',pagesize=(image_width,image_height))
b=background_color[0]
g = background_color[1]
r = background_color[2]
c.setFillColorRGB(r,g,b)
c.rect(0,0,image_width,image_height,fill=1)
c.setFillColor(black)
c.setStrokeColor(black)
for chain in words_list.keys():
    complete_list = words_list.get(chain)
    x,y,w,h,box = get_dimensions(complete_list)
    # x = x - w//2
    # y = y + h//2
    cropped = crop_img(draw,w+30,h+30,box)
    cv2.drawContours(draw,[box],0,(255,0,255),2)
    # cv2.rectangle(draw,(x,y),(x+w,y+h),(255,0,255),2)
    # cropped = image[y/:y+h,x:x+w]
    cv2.imwrite('cropped_word'+str(chain)+filename,cropped)
    text = pytesseract.image_to_string(cropped)
    print(text)
    c.setFont('Helvetica-Bold',(avg_h+avg_width))
    c.drawString(x/72,(image_height-y),text)
    # break
c.showPage()
c.save()
cv2.imwrite('draw.png',draw)
