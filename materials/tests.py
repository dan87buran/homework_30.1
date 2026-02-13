from django.test import TestCase

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson, Subscription

User = get_user_model()

class LessonTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title='Test Course',
            description='Course description'
        )

        self.lesson_data = {
            'title': 'Test Lesson',
            'description': 'Lesson description',
            'video_link': 'https://www.youtube.com/watch?v=12345',
            'course': self.course.id
        }

    def test_create_lesson_success(self):
        """Успешное создание урока с корректной YouTube-ссылкой."""
        response = self.client.post('/api/lessons/', self.lesson_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_create_lesson_invalid_youtube(self):
        """Попытка создать урок со ссылкой не на YouTube."""
        self.lesson_data['video_link'] = 'https://vimeo.com/12345'
        response = self.client.post('/api/lessons/', self.lesson_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_list_lessons(self):
        """Проверка получения списка уроков (с пагинацией)."""
        Lesson.objects.create(
            title='L1',
            description='D1',
            video_link='https://youtu.be/abc',
            course=self.course
        )
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)   # пагинация
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_lesson(self):
        """Получение одного урока."""
        lesson = Lesson.objects.create(
            title='L1',
            description='D1',
            video_link='https://youtu.be/abc',
            course=self.course
        )
        response = self.client.get(f'/api/lessons/{lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'L1')

    def test_update_lesson(self):
        """Обновление урока."""
        lesson = Lesson.objects.create(
            title='L1',
            description='D1',
            video_link='https://youtu.be/abc',
            course=self.course
        )
        lesson.owner = self.user
        lesson.save()

        updated_data = {
            'title': 'Updated',
            'description': 'New desc',
            'video_link': 'https://www.youtube.com/watch?v=xyz',
            'course': self.course.id
        }
        response = self.client.put(f'/api/lessons/{lesson.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, 'Updated')

    def test_delete_lesson(self):
        """Удаление урока."""
        lesson = Lesson.objects.create(
            title='L1',
            description='D1',
            video_link='https://youtu.be/abc',
            course=self.course
        )
        lesson.owner = self.user
        lesson.save()

        response = self.client.delete(f'/api/lessons/{lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='subscriber@example.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title='Course for sub',
            description='Some description'
        )

    def test_subscribe(self):
        """Подписка на курс."""
        response = self.client.post('/api/subscriptions/', {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe(self):
        """Отписка от курса."""
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post('/api/subscriptions/', {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_missing_course_id(self):
        """Ошибка, если не передан course_id."""
        response = self.client.post('/api/subscriptions/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_subscribed_field_in_course(self):
        """Проверка, что в курсе появилось поле is_subscribed."""
        # Подписываемся
        self.client.post('/api/subscriptions/', {'course_id': self.course.id})
        # Запрашиваем курс
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_is_subscribed_false_for_anonymous(self):
        """Для неавторизованного пользователя is_subscribed = False."""
        client = APIClient()   # без аутентификации
        response = client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

