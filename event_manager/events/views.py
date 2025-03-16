import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Event, Participant
from .forms import ParticipantForm


def event_list(request):
    """
    Отображает список всех мероприятий.
    """
    events = Event.objects.all()  # Получаем все мероприятия из базы данных
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, event_id):
    """Детали мероприятия и форма записи"""
    event = get_object_or_404(Event, id=event_id)
    participants = event.participants.all()

    if request.method == 'POST':
        return _handle_participant_form(request, event)

    return render(request, 'events/event_detail.html', {
        'event': event,
        'participants': participants,
        'form': ParticipantForm(),
        'average_age': _calculate_average_age(participants)
    })


# НОВЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
def _handle_participant_form(request, event):
    """Обработка формы участника"""
    form = ParticipantForm(request.POST)
    if form.is_valid():
        participant = form.save(commit=False)
        participant.event = event
        participant.save()
        event.participants_count += 1
        event.save()
        messages.success(request, 'Вы успешно записаны!')
        return redirect('event_detail', event_id=event.id)

    return render(request, 'events/event_detail.html', {
        'event': event,
        'form': form
    })


def _calculate_average_age(participants):
    """Расчет среднего возраста"""
    if not participants:
        return None
    return sum(p.age for p in participants) / len(participants)

def event_statistics(request):
    """
    Отображает статистику по мероприятиям.
    Если event_id указан, отображает статистику для конкретного мероприятия.
    """
    # Получаем все мероприятия
    events = Event.objects.all()

    # Получаем event_id из GET-запроса
    event_id = request.GET.get('event_id')

    # Если event_id указан, получаем конкретное мероприятие
    if event_id:
        event = get_object_or_404(Event, id=event_id)
        print(f"Выбрано мероприятие: {event.title}")  # Отладочное сообщение
    else:
        event = None
        print("Мероприятие не выбрано.")  # Отладочное сообщение

    # График 1: Количество участников по всем мероприятиям
    data_all_events = {
        'Название мероприятия': [event.title for event in events],
        'Количество участников': [event.participants_count for event in events],
        'Максимальное количество участников': [event.max_participants for event in events],
    }
    df_all_events = pd.DataFrame(data_all_events)

    # Группируем данные по названию мероприятия
    stats_all_events = df_all_events.groupby('Название мероприятия').agg({
        'Количество участников': 'sum',
        'Максимальное количество участников': 'sum',
    }).reset_index()

    # Создаем первый график
    plt.figure(figsize=(10, 6))
    plt.bar(stats_all_events['Название мероприятия'], stats_all_events['Количество участников'], label='Участники')
    plt.bar(stats_all_events['Название мероприятия'], stats_all_events['Максимальное количество участников'], label='Максимум', alpha=0.5)
    plt.xlabel('Название мероприятия')
    plt.ylabel('Количество участников')
    plt.title('Статистика по мероприятиям')
    plt.legend()

    # Сохраняем первый график в формате Base64
    buffer_all_events = BytesIO()
    plt.savefig(buffer_all_events, format='png')
    buffer_all_events.seek(0)
    image_all_events = base64.b64encode(buffer_all_events.getvalue()).decode('utf-8')
    plt.close()

    # График 2: Распределение участников по университетам (если мероприятие выбрано)
    image_universities = None
    if event:
        participants = event.participants.all()
        if participants:  # Проверяем, есть ли участники
            universities = [participant.university for participant in participants if
                            participant.university]  # Исключаем пустые значения
            if universities:  # Проверяем, есть ли университеты
                university_counts = pd.Series(universities).value_counts()

                # Создаем второй график
                plt.figure(figsize=(10, 6))
                university_counts.plot(kind='bar', color='skyblue', rot=0)  # rot=0 для горизонтальных подписей
                plt.xlabel('Университет')
                plt.ylabel('Количество участников')
                plt.title(f'Распределение участников по университетам ({event.title})')

                # Сохраняем второй график в формате Base64
                buffer_universities = BytesIO()
                plt.savefig(buffer_universities, format='png')
                buffer_universities.seek(0)
                image_universities = base64.b64encode(buffer_universities.getvalue()).decode('utf-8')
                plt.close()
            else:
                print("Нет данных по университетам для участников.")  # Отладочное сообщение
        else:
            print("Нет участников для выбранного мероприятия.")

    # Передаем данные в шаблон
    return render(request, 'events/statistics.html', {
        'events': events,
        'selected_event': event,
        'image_all_events': image_all_events,
        'image_universities': image_universities,
    })
