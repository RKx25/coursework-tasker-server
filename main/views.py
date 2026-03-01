from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from .models import Task
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer,
    SyncRequestSerializer, SyncResponseSerializer
)
import uuid

class TaskListAPIView(APIView):
    """
    GET: Получение всех задач
    POST: Создание новой задачи
    """
    
    def get(self, request):
        """Получение всех задач (исключая мягко удаленные)"""
        tasks = Task.objects.filter(is_deleted=False)
        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'tasks': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Создание новой задачи"""
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Генерируем ID для новой задачи
            task = Task.objects.create(
                id=str(uuid.uuid4()),
                **serializer.validated_data
            )
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailAPIView(APIView):
    """
    PUT: Обновление задачи
    DELETE: Удаление задачи
    """
    
    def get_object(self, task_id):
        try:
            return Task.objects.get(id=task_id, is_deleted=False)
        except Task.DoesNotExist:
            return None
    
    def put(self, request, task_id):
        """Обновление задачи"""
        task = self.get_object(task_id)
        if not task:
            return Response(
                {'error': 'Task not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            # Обновляем поля задачи
            for key, value in serializer.validated_data.items():
                setattr(task, key, value)
            task.version += 1
            task.save()
            
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, task_id):
        """Удаление задачи (мягкое удаление)"""
        try:
            task = Task.objects.get(id=task_id, is_deleted=False)
            task.is_deleted = True
            task.version += 1
            task.save()
            return Response({
                'success': True,
                'id': task_id
            }, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({
                'success': False,
                'id': task_id,
                'error': 'Task not found'
            }, status=status.HTTP_404_NOT_FOUND)

class TaskSyncAPIView(APIView):
    """
    POST: Синхронизация задач с клиентом
    """
    
    def post(self, request):
        serializer = SyncRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        client_tasks = data.get('tasks', [])
        last_sync = data.get('lastSync')
        
        with transaction.atomic():
            # Обработка задач от клиента
            for task_data in client_tasks:
                task_id = task_data.get('id')
                
                if task_id:
                    # Обновление существующей задачи
                    try:
                        task = Task.objects.get(id=task_id)
                        # Обновляем поля, если версия клиента новее
                        if task_data.get('version', 0) > task.version:
                            for key, value in task_data.items():
                                if key not in ['id', 'createdAt', 'updatedAt']:
                                    # Конвертируем имена полей обратно в snake_case для модели
                                    if key == 'dueDate':
                                        setattr(task, 'due_date', value)
                                    elif key == 'createdAt':
                                        setattr(task, 'created_at', value)
                                    elif key == 'updatedAt':
                                        setattr(task, 'updated_at', value)
                                    else:
                                        setattr(task, key, value)
                            task.version += 1
                            task.save()
                    except Task.DoesNotExist:
                        # Создание новой задачи
                        task_data['version'] = 1
                        # Конвертируем имена полей
                        if 'dueDate' in task_data:
                            task_data['due_date'] = task_data.pop('dueDate')
                        Task.objects.create(**task_data)
            
            # Получение изменений для клиента
            tasks_query = Task.objects.filter(is_deleted=False)
            if last_sync:
                tasks_query = tasks_query.filter(updated_at__gt=last_sync)
            
            # Формирование ответа
            response_data = {
                'tasks': TaskSerializer(tasks_query, many=True).data,
                'lastSync': timezone.now()
            }
            
            response_serializer = SyncResponseSerializer(data=response_data)
            response_serializer.is_valid()
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)