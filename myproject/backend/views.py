from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from .serializers import ImageUploadSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Image
from .serializers import ImageSerializer

from .serializers import PreferenceSerializer
from .models import UserPreference
import uuid  

import pytesseract

import cv2
import numpy as np
from django.conf import settings
import os
from rest_framework import status
import re
from transformers import pipeline
import torch
import easyocr

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.core.files.base import ContentFile

from PIL import Image, ImageEnhance, ImageOps
import io
import json

from backend.models import UserPreference

# Initialize EasyOCR - more accurate than Tesseract
try:
    ocr_reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if you have CUDA
    EASYOCR_AVAILABLE = True
    print("EasyOCR initialized successfully")
except Exception as e:
    print(f"Warning: EasyOCR not available: {e}")
    ocr_reader = None
    EASYOCR_AVAILABLE = False

# Initialize Hugging Face models - better for sign detection
try:
    # For object detection - using YOLO-based model for better accuracy
    object_detector = pipeline("object-detection", model="hustvl/yolos-tiny")
    # For image classification - to identify sign types
    image_classifier = pipeline("image-classification", model="microsoft/resnet-50")
    AI_MODEL_AVAILABLE = True
    print("Hugging Face models initialized successfully")
except Exception as e:
    print(f"Warning: Could not load AI models: {e}")
    object_detector = None
    image_classifier = None
    AI_MODEL_AVAILABLE = False

def detect_road_signs(text):
    """Detect road signs and traffic signs from OCR text"""
    signs = []
    text_lower = text.lower()
    
    # Common road signs patterns
    sign_patterns = {
        'stop': ['stop', 'stop sign'],
        'yield': ['yield', 'give way'],
        'speed_limit': ['speed limit', 'mph', 'km/h', r'\d+\s*mph', r'\d+\s*km/h'],
        'no_entry': ['no entry', 'do not enter', 'authorized personnel only'],
        'one_way': ['one way', 'one-way'],
        'parking': ['parking', 'no parking', 'p'],
        'caution': ['caution', 'warning', 'danger', 'careful'],
        'school': ['school', 'children', 'school zone'],
        'construction': ['construction', 'work zone', 'men at work'],
        'exit': ['exit', 'way out'],
        'entrance': ['entrance', 'enter']
    }
    
    for sign_type, patterns in sign_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                signs.append({
                    'type': sign_type,
                    'text': pattern,
                    'confidence': 0.8
                })
                break
    
    return signs

def detect_visual_objects(image_path):
    """Enhanced object detection using Hugging Face models"""
    if not AI_MODEL_AVAILABLE:
        return []
    
    try:
        from PIL import Image
        image = Image.open(image_path)
        
        detected_objects = []
        
        # Object detection with YOLO
        if object_detector:
            results = object_detector(image)
            for result in results:
                label = result['label'].lower()
                score = result['score']
                
                # Focus on traffic-related objects with lower threshold for better detection
                if any(keyword in label for keyword in ['sign', 'car', 'truck', 'bus', 'person', 'bicycle', 'motorcycle', 'traffic']):
                    if score > 0.3:  # Lower threshold for better detection
                        detected_objects.append({
                            'object': result['label'],
                            'confidence': round(score, 2),
                            'bbox': result['box'],
                            'type': 'object_detection'
                        })
        
        # Image classification for sign types
        if image_classifier:
            classifications = image_classifier(image, top_k=5)
            for result in classifications:
                label = result['label'].lower()
                score = result['score']
                
                # Look for sign-related classifications
                if any(keyword in label for keyword in ['sign', 'traffic', 'stop', 'warning', 'speed', 'parking']):
                    if score > 0.1:  # Even lower threshold for classification
                        detected_objects.append({
                            'object': result['label'],
                            'confidence': round(score, 2),
                            'type': 'classification'
                        })
        
        return detected_objects
    except Exception as e:
        print(f"Error in visual object detection: {e}")
        return []

def generate_sign_alerts(detected_signs):
    """Generate specific audio alerts for detected signs"""
    alerts = []
    
    alert_messages = {
        'stop': "Stop sign ahead. Stop carefully and check for traffic.",
        'yield': "Yield sign detected. Slow down and yield to oncoming traffic.",
        'speed_limit': "Speed limit sign detected. Please check your current speed.",
        'no_entry': "No entry sign ahead. Do not proceed in this direction.",
        'one_way': "One way street detected. Check traffic direction.",
        'caution': "Caution sign ahead. Proceed with extra care.",
        'school': "School zone detected. Reduce speed and watch for children.",
        'construction': "Construction zone ahead. Slow down and follow posted signs.",
        'parking': "Parking sign detected.",
        'exit': "Exit sign detected.",
        'entrance': "Entrance sign detected.",
        'default': "Traffic sign detected. Please proceed with caution."
    }
    
    for sign in detected_signs:
        sign_type = sign.get('type', 'default')
        message = alert_messages.get(sign_type, alert_messages['default'])
        alerts.append({
            'type': sign_type,
            'message': message,
            'confidence': sign.get('confidence', 0.5)
        })
    
    return alerts

def generate_audio_message(text, detected_signs):
    """Generate comprehensive audio message including text and sign alerts"""
    messages = []
    
    # Add sign-specific alerts first (higher priority)
    if detected_signs:
        for sign in detected_signs:
            sign_type = sign.get('type')
            if sign_type == 'stop':
                messages.append("STOP SIGN detected! Come to a complete stop.")
            elif sign_type == 'yield':
                messages.append("YIELD SIGN detected! Slow down and yield to traffic.")
            elif sign_type == 'speed_limit':
                messages.append("SPEED LIMIT SIGN detected! Check your speed.")
            elif sign_type == 'no_entry':
                messages.append("NO ENTRY SIGN detected! Do not proceed.")
            elif sign_type == 'caution':
                messages.append("CAUTION SIGN detected! Proceed carefully.")
            elif sign_type == 'school':
                messages.append("SCHOOL ZONE SIGN detected! Reduce speed.")
            else:
                messages.append(f"{sign_type.replace('_', ' ').title()} sign detected.")
    
    # Add text content
    if text and text != "No text detected in image":
        if detected_signs:
            messages.append(f"Sign text reads: {text}")
        else:
            messages.append(f"Text detected: {text}")
    elif not detected_signs:
        messages.append("Image processed successfully.")
    
    return " ".join(messages)





@api_view(['GET'])
def root_api(request):
    return Response({"status": "API is running"})  


@api_view(['GET'])
def hello_api(request):
    return Response({"message": "Hello from Django API!"})


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    serializer = ImageUploadSerializer(data=request.data)
    if serializer.is_valid():
        image = serializer.validated_data['image']

        # Save file temporarily
        file_path = default_storage.save(image.name, image)
        file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # ---- Step 1: Read with OpenCV ----
        img = cv2.imread(file_full_path)

        # ---- Step 2: Apply multiple preferences ----
        applied_filters = []

        # Try to get "preferences" from request body
        preferences = request.data.getlist("preferences")  # works if sent as form-data keys
        if not preferences:
            preferences = request.data.get("preferences")  # works if JSON body
            if isinstance(preferences, str):
                try:
                    import json
                    preferences = json.loads(preferences)  # if stringified
                except:
                    preferences = [preferences]
        if not preferences:
            preferences = []  # fallback

        for pref in preferences:
            if pref == "deuteranopia":
                if len(img.shape) == 3:  # only convert if color image
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = cv2.equalizeHist(img)
                applied_filters.append("deuteranopia filter applied")

            elif pref == "protanopia":
                img = cv2.bitwise_not(img)
                applied_filters.append("protanopia filter applied")

            elif pref == "tritanopia":
                if len(img.shape) == 3:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                else:
                    gray = img
                _, img = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
                applied_filters.append("tritanopia filter applied")

            elif pref == "grayscale":
                if len(img.shape) == 3:  # only convert if color image
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                applied_filters.append("grayscale applied")

            else:
                applied_filters.append(f"{pref} not recognized")

        if not applied_filters:
            applied_filters.append("no preference set")

                # ---- Step 3: EasyOCR Text Detection ----
        ocr_results = []
        
        if EASYOCR_AVAILABLE and ocr_reader:
            try:
                # EasyOCR works directly on the image file
                results = ocr_reader.readtext(file_full_path)
                
                # Extract text with confidence scores and bounding boxes
                for (bbox, text_detected, confidence) in results:
                    if confidence > 0.5 and len(text_detected.strip()) > 1:  # Filter low confidence
                        # Calculate center Y coordinate for sorting (top to bottom)
                        center_y = (bbox[0][1] + bbox[2][1]) / 2
                        ocr_results.append({
                            'text': text_detected.strip(),
                            'confidence': round(confidence, 2),
                            'bbox': bbox,
                            'center_y': center_y,
                            'center_x': (bbox[0][0] + bbox[2][0]) / 2
                        })
                
                # Combine all detected text in proper reading order
                if ocr_results:
                    # Sort by reading order: top to bottom, then left to right
                    def sort_reading_order(item):
                        # Group by approximate line (within 20 pixels vertically)
                        line_height = 20
                        line_group = int(item['center_y'] / line_height)
                        return (line_group, item['center_x'])
                    
                    ocr_results.sort(key=sort_reading_order)
                    
                    # Group text by lines and join with line breaks
                    lines = []
                    current_line = []
                    current_line_group = None
                    
                    for result in ocr_results:
                        line_height = 20
                        line_group = int(result['center_y'] / line_height)
                        
                        if current_line_group is None or line_group == current_line_group:
                            current_line.append(result['text'])
                            current_line_group = line_group
                        else:
                            # New line detected
                            if current_line:
                                lines.append(' '.join(current_line))
                            current_line = [result['text']]
                            current_line_group = line_group
                    
                    # Add the last line
                    if current_line:
                        lines.append(' '.join(current_line))
                    
                    text = '\n'.join(lines)  # Join lines with line breaks
                else:
                    text = "No text detected in image"
                    
            except Exception as e:
                print(f"EasyOCR Error: {e}")
                text = "OCR processing failed"
        else:
            text = "EasyOCR not available"
        
        # ---- Step 4: Visual Object Detection & Sign Classification ----
        visual_objects = detect_visual_objects(file_full_path)
        
        # Enhanced sign detection from OCR text and visual objects
        detected_signs = []
        sign_alerts = []
        
        # Analyze OCR text for sign types
        if text and text.strip() != "No text detected in image":
            text_lower = text.lower()
            
            # Check for specific sign types in the text
            if 'stop' in text_lower:
                detected_signs.append({'type': 'stop', 'confidence': 0.9, 'source': 'text'})
            elif any(word in text_lower for word in ['yield', 'give way']):
                detected_signs.append({'type': 'yield', 'confidence': 0.8, 'source': 'text'})
            elif any(word in text_lower for word in ['speed', 'limit', 'mph', 'km/h']):
                detected_signs.append({'type': 'speed_limit', 'confidence': 0.8, 'source': 'text'})
            elif any(word in text_lower for word in ['no entry', 'do not enter', 'authorized']):
                detected_signs.append({'type': 'no_entry', 'confidence': 0.8, 'source': 'text'})
            elif 'one way' in text_lower:
                detected_signs.append({'type': 'one_way', 'confidence': 0.8, 'source': 'text'})
            elif any(word in text_lower for word in ['caution', 'warning', 'danger']):
                detected_signs.append({'type': 'caution', 'confidence': 0.7, 'source': 'text'})
            elif any(word in text_lower for word in ['school', 'children']):
                detected_signs.append({'type': 'school', 'confidence': 0.8, 'source': 'text'})
            elif any(word in text_lower for word in ['construction', 'work zone', 'road work']):
                detected_signs.append({'type': 'construction', 'confidence': 0.8, 'source': 'text'})
            elif any(word in text_lower for word in ['parking', 'no parking', 'park']):
                detected_signs.append({'type': 'parking', 'confidence': 0.7, 'source': 'text'})
            elif 'exit' in text_lower:
                detected_signs.append({'type': 'exit', 'confidence': 0.7, 'source': 'text'})
        
        # Generate alerts for detected signs
        if detected_signs:
            sign_alerts = generate_sign_alerts(detected_signs)


        # ---- Step 6: Save processed image ----
        processed_filename = f"processed_{uuid.uuid4().hex}.png"
        processed_path = os.path.join(settings.MEDIA_ROOT, processed_filename)
        cv2.imwrite(processed_path, img)

        processed_image_url = request.build_absolute_uri(
            os.path.join(settings.MEDIA_URL, processed_filename)
        )

        # ---- Response ----
        return Response({
            "message": "Image processed successfully",
            "applied_filters": applied_filters,
            "processed_image_url": processed_image_url,
            "extracted_text": text.strip(),
            "visual_objects": visual_objects,
            "audio_message": generate_audio_message(text.strip(), detected_signs),
            "detected_signs": detected_signs,
            "sign_alerts": sign_alerts,
            "easyocr_available": EASYOCR_AVAILABLE,
            "ocr_details": ocr_results if EASYOCR_AVAILABLE else [],
            "ai_model_available": AI_MODEL_AVAILABLE
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def set_preference(request):
    serializer = PreferenceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Preference saved",
            "type": serializer.data['type']
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

