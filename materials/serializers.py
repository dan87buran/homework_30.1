from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели :model:`materials.Lesson`.
    """
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner',)  # владелец проставляется автоматически


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели :model:`materials.Course`.

    **Динамические поля**
    * ``lessons_count`` — количество уроков в курсе (вычисляемое).
    * ``lessons`` — список уроков, вложенный сериализатор.
    """
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source='lessons')

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner',)

    def get_lessons_count(self, obj):
        """Возвращает количество уроков, связанных с курсом."""
        return obj.lessons.count()