from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from .serializers import ImageUploadSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import PreferenceSerializer
from .models import UserPreference
import uuid  

import pytesseract

import cv2
import pytesseract
import numpy as np
from django.conf import settings
import os
from rest_framework import status

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.core.files.base import ContentFile

from PIL import Image, ImageEnhance, ImageOps
import pytesseract
import io
import json

from backend.models import UserPreference

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"




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

                # ---- Step 3: Preprocess for OCR ----
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Denoise (helps reduce background specks)
        gray = cv2.medianBlur(gray, 3)

        # Adaptive Threshold (better for variable lighting)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 2
        )

        # Optionally upscale for OCR clarity
        resized = cv2.resize(thresh, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

        # ---- Step 4: OCR ----
        custom_config = r'--oem 3 --psm 6 -l eng'
        text = pytesseract.image_to_string(resized, config=custom_config)


        # ---- Step 5: Save processed image ----
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
            "extracted_text": text.strip()
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

