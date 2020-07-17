import cv2
import numpy as np

def gcd(a,b):
    if(b==0):
        return a
    else:
        return gcd(b,a%b)


def read_image(filename):
    image = cv2.imread(filename)
    image_height,image_width,_ = image.shape
    gc = gcd(image_width,image_height)
    if(image_height+image_width > 2500 and gc != 1):
        hr = image_height//gc
        wr = image_width//gc
        mul = gc//2
        image = cv2.resize(image,(wr*mul,hr*mul),interpolation=cv2.INTER_AREA)
    background_color = image[0,0]
    # print(len(background_color))
    img_gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(img_gray,(7,7),1.75)
    v = np.mean(blur)
    # print(v)
    lower = v//2
    upper = v//2 + 20
    canny = cv2.Canny(blur,lower,upper)
    return image,img_gray,v,canny
