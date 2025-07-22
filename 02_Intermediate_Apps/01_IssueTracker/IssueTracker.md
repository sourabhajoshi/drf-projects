# Django REST Framework — Issue Tracker API

This project demonstrates a full-featured API using Django REST Framework covering:

- One-to-One and One-to-Many Models
- ModelSerializers
- ViewSets
- Search, Filter & Ordering
- Pagination
- Custom Permissions

Step 1: Project Setup
```
django-admin startproject tracker
cd tracker
python -m venv venv && source venv/bin/activate
pip install django djangorestframework django-filter
python manage.py startapp issues
```

Step 2: Update settings.py
```
# tracker/settings.py

INSTALLED_APPS = [
    ...
    'rest_framework',       # Enable Django REST Framework
    'django_filters',       # Enable django-filter for advanced filtering
    'issues',               # Your custom app
]

# Global DRF configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],  # Default: login required
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,  # Default page size for paginated responses
}

```

Step 3: Models
```
# issues/models.py

from django.db import models
from django.contrib.auth.models import User

# One-to-One relationship: Each user has one profile
class UserProfile(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.URLField(blank=True)
    bio    = models.TextField(blank=True)

# Each user can own multiple projects (One-to-Many)
class Project(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)

# Each project can have many issues (One-to-Many)
class Issue(models.Model):
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reported_issues")
    assignee    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues")
    state       = models.CharField(max_length=20, choices=[("open","Open"),("closed","Closed")], default="open")
    priority    = models.IntegerField(default=2)  # 1=high, 2=normal, 3=low
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

# Each issue can have multiple comments
class Comment(models.Model):
    issue      = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


<!-- Migrate the changes -->
python manage.py makemigrations
python manage.py migrate

```

Step 4: Serializers
```
# issues/serializers.py

from rest_framework import serializers
from .models import UserProfile, Project, Issue, Comment
from django.contrib.auth.models import User

# Simple serializer for profile data
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["avatar", "bio"]

# Extends User with nested profile
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]

# Comment serializer with string author field
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "body", "created_at"]

# Issue serializer with nested comments and read-only creator
class IssueSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    comments   = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = "__all__"

# Project serializer with nested issues
class ProjectSerializer(serializers.ModelSerializer):
    owner  = serializers.StringRelatedField(read_only=True)
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

```

Step 5: Custom Permission
```
# issues/permissions.py

from rest_framework import permissions

# Only allow owners to edit their own projects
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Anyone can read
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only owner or admin can modify
        return obj.owner == request.user or request.user.is_staff
```

Step 6: Filters
```
# issues/filters.py

from django_filters import rest_framework as filters
from .models import Issue

# Enables filtering by priority, state, assignee
class IssueFilter(filters.FilterSet):
    class Meta:
        model = Issue
        fields = ["state", "priority", "assignee"]

```

Step 7: ViewSets
```
# issues/views.py

from rest_framework import viewsets, permissions, filters as drf_filters
from .models import Project, Issue, Comment
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly
from .filters import IssueFilter
from django_filters.rest_framework import DjangoFilterBackend

# Project ViewSet with search, ordering, permission
class ProjectViewSet(viewsets.ModelViewSet):
    queryset           = Project.objects.all()
    serializer_class   = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends    = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields      = ["name", "description"]
    ordering_fields    = ["name", "id"]

    # Set owner to the current user
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Issue ViewSet with filtering, search, ordering
class IssueViewSet(viewsets.ModelViewSet):
    queryset           = Issue.objects.all()
    serializer_class   = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class    = IssueFilter
    search_fields      = ["title", "description"]
    ordering_fields    = ["priority", "created_at"]

    # Set created_by to logged-in user
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Comment ViewSet with simple ordering
class CommentViewSet(viewsets.ModelViewSet):
    queryset           = Comment.objects.all()
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [drf_filters.OrderingFilter]
    ordering_fields    = ["created_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

```

Step 8: Routers
```
<!-- issues/urls.py : App -->

from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, IssueViewSet, CommentViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet)
router.register("issues", IssueViewSet)
router.register("comments", CommentViewSet)

urlpatterns = router.urls


<!-- tracker/urls.py -->

from django.urls import path, include

urlpatterns = [
    path("api/", include("issues.urls")),
    path("api-auth/", include("rest_framework.urls")),
]

```

Step 9: Test the API
| Endpoint                                 | Description                  |
| ---------------------------------------- | ---------------------------- |
| `POST /api/projects/`                    | Create a project             |
| `GET /api/issues/?search=bug`            | Search issues                |
| `GET /api/issues/?priority=1&state=open` | Filter issues                |
| `GET /api/issues/`                       | Paginated issue list         |
| `PATCH /api/projects/{id}/`              | Only allowed for owner/admin |
