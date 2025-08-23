import easyocr

reader = easyocr.Reader(['en'])  # load English
results = reader.readtext('sample2.jpg')

for (bbox, text, prob) in results:
    print(f"Detected text: {text} (confidence: {prob:.2f})")
