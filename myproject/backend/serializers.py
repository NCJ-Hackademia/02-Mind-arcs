from rest_framework import serializers
from .models import UserPreference
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image', 'preferences', 'ocr_language']


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'type'] 
        
class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()