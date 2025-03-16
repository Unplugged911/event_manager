from django.test import RequestFactory, TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .views import event_detail
from .models import Event, Participant
from .forms import ParticipantForm
from unittest.mock import patch

class AddParticipantTest(TestCase):
    def setUp(self):
        # Создаем тестовое мероприятие
        self.event = Event.objects.create(
            title="Тестовое мероприятие",
            type="conference",
            date="2023-12-31T23:59:59Z",
            location="Тестовое место",
            description="Тестовое описание",
            max_participants=100,
            participants_count=0,
        )
        self.client = Client()  # Используем Client вместо RequestFactory
        self.factory = RequestFactory()

    @patch('events.views.ParticipantForm')  # Мокируем форму
    def test_add_participant_valid_form(self, mock_form):
        # Мокируем поведение формы
        mock_form_instance = mock_form.return_value
        mock_form_instance.is_valid.return_value = True  # Форма валидна
        mock_form_instance.save.return_value = Participant(
            event=self.event,
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            age=25,
            university="Тестовый университет",
            faculty="Тестовый факультет",
            group="Группа 1",
        )

        # Создаем POST-запрос с валидными данными
        response = self.client.post(reverse('event_detail', args=[self.event.id]), {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'age': 25,
            'university': 'Тестовый университет',
            'faculty': 'Тестовый факультет',
            'group': 'Группа 1',
        })

        # Проверяем, что участник был добавлен
        self.event.refresh_from_db()  # Обновляем данные мероприятия из базы
        self.assertEqual(self.event.participants_count, 1)  # Счетчик участников увеличился
        mock_form_instance.save.assert_called_once()  # Форма была сохранена
        self.assertEqual(response.status_code, 302)  # Редирект после успешной записи
        self.assertEqual(response.url, reverse('event_detail', args=[self.event.id]))  # Редирект на ту же страницу

        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Вы успешно записаны на мероприятие!')

    @patch('events.views.ParticipantForm')  # Мокируем форму
    def test_add_participant_invalid_form(self, mock_form):
        # Мокируем поведение формы
        mock_form_instance = mock_form.return_value
        mock_form_instance.is_valid.return_value = False  # Форма невалидна

        # Создаем POST-запрос с невалидными данными
        response = self.client.post(reverse('event_detail', args=[self.event.id]), {
            'first_name': '',  # Пустое имя
            'last_name': 'Иванов',
            'email': 'invalid-email',  # Некорректный email
            'age': -5,  # Отрицательный возраст
            'university': 'Тестовый университет',
            'faculty': 'Тестовый факультет',
            'group': 'Группа 1',
        })

        # Проверяем, что участник не был добавлен
        self.event.refresh_from_db()  # Обновляем данные мероприятия из базы
        self.assertEqual(self.event.participants_count, 0)  # Счетчик участников не изменился
        mock_form_instance.save.assert_not_called()  # Форма не была сохранена
        self.assertEqual(response.status_code, 200)  # Страница отображается снова
        self.assertIn('form', response.context)  # Форма передается в контекст