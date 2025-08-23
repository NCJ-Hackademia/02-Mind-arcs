from rest_framework import serializers

from .models import UserPreference

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'type'] 
        
class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()