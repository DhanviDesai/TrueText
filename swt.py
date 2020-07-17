import numpy as np
import cv2

def cal_swt(img_gray,canny,type):
    sobelx = cv2.Sobel(img_gray,cv2.CV_64F,1,0,ksize=-1)
    sobely = cv2.Sobel(img_gray,cv2.CV_64F,0,1,ksize=-1)
    step_x = -1 * sobelx
    step_y = -1 * sobely
    mag_g = np.sqrt(step_x * step_x + step_y * step_y)
    grad_x_g = step_x/(mag_g + 1e-10)
    grad_y_g = step_y/(mag_g + 1e-10)
    swt = np.full((canny.shape),np.Infinity)
    h = canny.shape[0]
    w = canny.shape[1]
    rays = []
    for x in range(canny.shape[1]):
        for y in range(canny.shape[0]):
            if(canny[y,x] > 0):
                #found an edge pixel here
                dx = sobelx[y,x]
                dy = sobely[y,x]
                grad_x = grad_x_g[y,x]
                grad_y = grad_y_g[y,x]
                prev_x,prev_y,i = x,y,0
                ray = []
                ray.append((x,y))
                count = 0
                while True:
                    i+=1
                    if(type):
                        cur_x = int(np.floor(x + i * grad_x))
                        cur_y = int(np.floor(y + i * grad_y))
                    else:
                        cur_x = int(np.floor(x - i * grad_x))
                        cur_y = int(np.floor(y - i * grad_y))
                    if(cur_x == prev_x and cur_y == prev_y):
                        break
                    else:
                        try:
                            if(canny[cur_y,cur_x] > 0):
                                ray.append((cur_x,cur_y))
                                if(np.arccos(grad_x * -grad_x_g[cur_y,cur_x] + grad_y * -grad_y_g[cur_y,cur_x]) < np.pi/2):
                                    thickness = np.sqrt((cur_x - x )**2 + (cur_y - y)**2)
                                    for (rx,ry) in ray:
                                        swt[ry,rx] = min(thickness,swt[ry,rx])
                                    rays.append(ray)
                                break
                            ray.append((cur_x,cur_y))
                        except:
                            break
                        prev_x = cur_x
                        prev_y = cur_y

    for ray in rays:
        median = np.median([swt[y,x] for (x,y) in ray])
        for (x,y) in ray:
            swt[y,x] = min(median,swt[y,x])
    return swt,sobelx,sobely
