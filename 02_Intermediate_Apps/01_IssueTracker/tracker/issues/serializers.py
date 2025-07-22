from rest_framework import serializers
from .models import UserProfile, Project, Issue, Comment
from django.contrib.auth.models import User

# Serializer for profile data
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["avatar", "bio"]
        

# Extend serializer with nested profile
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]
        
class ProjectSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Project
        