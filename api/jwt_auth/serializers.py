from typing import Type
from django.db.models.base import Model
from rest_framework import serializers

# from django.contrib.auth.models import User  # 
from django.contrib.auth import get_user_model



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance= self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
