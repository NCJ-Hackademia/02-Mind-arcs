import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ocr_on_boxes(image, boxes):
    texts = []

    for (x, y, w, h) in boxes:
        roi = image[y:y+h, x:x+w]

        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        text = pytesseract.image_to_string(roi_rgb, config='--oem 3 --psm 6')
        text = text.strip()

        if text:
            texts.append(text)

    return texts
