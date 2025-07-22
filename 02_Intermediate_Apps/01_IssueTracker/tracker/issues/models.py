from django.db import models
from django.contrib.auth.models import User

# one to one : each user has one profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    
# Each user can own multiple projects (one-to-many)
class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
#Each project can have multiple issues (one-to-many)
class Issue(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reported_issues")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issue")
    state = models.CharField(max_length=20, choices=[
        ("open", "Open"),
        ("closed", "Closed")
    ], default="open")
    priority = models.IntegerField(default=2)  #high, normal and low
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
# each issue will have multiple comments
class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    auther = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
