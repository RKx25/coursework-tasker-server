from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    dueDate = serializers.DateTimeField(source='due_date', required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed', 
            'priority', 'dueDate', 'createdAt', 'updatedAt', 'version'
        ]
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},  # Разрешаем передавать ID для синхронизации
            'version': {'read_only': False, 'required': False}
        }

class TaskCreateSerializer(serializers.ModelSerializer):
    dueDate = serializers.DateTimeField(source='due_date', required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'priority', 'dueDate']
        extra_kwargs = {
            'title': {'required': True},
            'completed': {'required': False, 'default': False},
            'priority': {'required': False, 'default': 'medium'}
        }

class TaskUpdateSerializer(serializers.ModelSerializer):
    dueDate = serializers.DateTimeField(source='due_date', required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'priority', 'dueDate']
        extra_kwargs = {
            'title': {'required': False},
            'completed': {'required': False},
            'priority': {'required': False}
        }

class SyncRequestSerializer(serializers.Serializer):
    tasks = TaskSerializer(many=True, required=False, default=list)
    lastSync = serializers.DateTimeField(required=False, allow_null=True)

class SyncResponseSerializer(serializers.Serializer):
    tasks = TaskSerializer(many=True)
    lastSync = serializers.DateTimeField()