import cv2
import numpy as np

def preprocess_image(image_path):
    img = cv2.imread(image_path)


    scale_percent = 100 
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    img = cv2.resize(img, (width, height))


    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    grayscale = cv2.GaussianBlur(grayscale, (3, 3), 0)

    grayscale = cv2.equalizeHist(grayscale)

    return img, grayscale

def detect_text_regions(gray):
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        15, 10
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 20 and h > 20:  
            boxes.append((x, y, w, h))

    return boxes, thresh
