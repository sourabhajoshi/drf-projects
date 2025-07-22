from django.db import models

# Create your models here.
class Task(models.Model):
    STATE_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("in_qa", "In QA"),
        ("done", "Done"),
    ]
    
    title = models.CharField(max_length=25)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="planning")
    priority = models.IntegerField(default=0)
    points = 
