from django.db import models
from django.utils import timezone
import uuid

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='Title', default="task")
    description = models.TextField(blank=True, verbose_name='Description')
    completed = models.BooleanField(default=False, verbose_name='Completed')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Due Date')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Поля для синхронизации
    last_sync = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    version = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'version': self.version
        }