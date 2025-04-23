from django.urls import path
from .views import (
    CourseListAPIView, DepartmentListAPIView, LinkExtractAPIView,
    CategoryCoursesAPIView, CourseResourcesAPIView, AuthenticatedResourcesAPIView,
    MoodleCoursesAPIView, MoodleLoginAPIView, MoodleCoursePDFsAPIView
)
from .mock_views import MockAuthResourcesAPIView

urlpatterns = [
    path('courses/', CourseListAPIView.as_view(), name='course-list'),
    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path('links/', LinkExtractAPIView.as_view(), name='link-extract'),
    path('category/<int:category_id>/courses/', CategoryCoursesAPIView.as_view(), name='category-courses'),
    path('course/<int:course_id>/resources/', CourseResourcesAPIView.as_view(), name='course-resources'),
    path('resources/', CourseResourcesAPIView.as_view(), name='course-resources-post'),
    path('auth-resources/', AuthenticatedResourcesAPIView.as_view(), name='authenticated-resources'),
    path('mock-auth-resources/', MockAuthResourcesAPIView.as_view(), name='mock-authenticated-resources'),
    path('moodle-courses/', MoodleCoursesAPIView.as_view(), name='moodle-courses'),
    path('moodle-login/', MoodleLoginAPIView.as_view(), name='moodle-login'),
    path('moodle-pdfs/', MoodleCoursePDFsAPIView.as_view(), name='moodle-pdfs'),
    path('moodle-pdfs/<str:course_id>/', MoodleCoursePDFsAPIView.as_view(), name='moodle-pdfs-detail'),
]
