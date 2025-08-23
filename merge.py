import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Preprocessing

def preprocess(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.equalizeHist(gray)
    return img, gray


# Text Detection

def detect_text(gray):
    thresh = cv2.adaptiveThreshold(gray, 255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,15, 10)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 20 and h > 20:  # filter tiny boxes
            boxes.append((x, y, w, h))
    return boxes

# OCR on detected boxes

def ocr_boxes(img, boxes):
    texts = []
    for (x, y, w, h) in boxes:
        roi = img[y:y+h, x:x+w]
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(roi_rgb, config='--oem 3 --psm 6').strip()
        if text:
            texts.append(text)
    return texts


# Visualization 

def visualize(img, boxes, texts):
    for i, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if i < len(texts):
            cv2.putText(img, texts[i], (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imshow("Detected Text", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Main pipeline

if __name__ == "__main__":
    image_path = "sample2.jpg" 
    img, gray = preprocess(image_path)
    boxes = detect_text(gray)
    texts = ocr_boxes(img, boxes)
    print("Detected texts:", texts)
    visualize(img, boxes, texts)
