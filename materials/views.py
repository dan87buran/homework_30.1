from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class LessonListCreateView(ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer