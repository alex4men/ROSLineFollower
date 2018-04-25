#!/usr/bin/env python
import cv2
import numpy as np



# Define a class to receive the characteristics of each line detection
class Line():
    def __init__(self, img):
        # was the line detected in the last iteration?
        # self.detected = False  
        # # x values of the last n fits of the line
        # self.recent_xfitted = [] 
        # #average x values of the fitted line over the last n iterations
        # self.bestx = None     
        # #polynomial coefficients averaged over the last n iterations
        # self.best_fit = None  
        # #polynomial coefficients for the most recent fit
        # self.current_fit = [np.array([False])]  
        self.window_center = img.shape[1]//2
        self.window_width = img.shape[1]//5
        self.seeBelowY = img.shape[0] - img.shape[0]//6
        self.img_centerX = img.shape[1]//2


    def find_offset(self, img):

        

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        
        
        windowLeftX = self.window_center-self.window_width
        windowRightX = self.window_center+self.window_width
        roi = gray[self.seeBelowY:,windowLeftX:windowRightX]
        thresh, binary = cv2.threshold(roi, 1, 255, cv2.THRESH_OTSU)
        binary_inv = np.zeros_like(binary)
        binary_inv[binary==0] = 1

        nonzero = binary_inv.nonzero()
        nonzerox = np.array(nonzero[1])

        outImg = img.copy()
        cv2.rectangle(outImg, (windowLeftX, self.seeBelowY), (windowRightX, gray.shape[0]), (0,255,0), 2)

        avgX = np.median(nonzerox)

        line_center = int(avgX)+windowLeftX
        cv2.circle(outImg, (line_center, self.seeBelowY), 5, (0,255,0),2)
        cv2.circle(outImg, (self.img_centerX, self.seeBelowY), 5, (0,0,255),2)

        if abs(self.window_center-line_center) > 10:
            self.window_center = int(0.5*line_center + 0.5*self.window_center)


        cte = line_center - self.img_centerX

        return cte, outImg


def main():
    img = cv2.imread('1.jpg')
    cv2.imshow('test', img)

    line = Line(img)
    cte, outImg = line.find_offset(img)

    cv2.imshow('testOut', outImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()