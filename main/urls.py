from django.urls import path
from .views import TaskListAPIView, TaskDetailAPIView, TaskSyncAPIView

urlpatterns = [
    # Основные endpoints
    path('api/tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('api/tasks/<str:task_id>/', TaskDetailAPIView.as_view(), name='task-detail'),
    
    # Синхронизация
    path('api/tasks/sync/', TaskSyncAPIView.as_view(), name='task-sync'),
]