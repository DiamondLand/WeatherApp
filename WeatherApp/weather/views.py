import requests

from django.shortcuts import render

from .models import City
from .forms import CityForm


def index(request):
    api_key = 'c269502293174e07abe130103242207'
    url = 'https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no'

    cities = City.objects.all()  #* Получаем все данные из базы
    all_cities = []  #* Общий список данных о погоде для передачи на фронт
    error_message = None

    if request.method == 'POST':
        form = CityForm(request.POST)
        city_name = form.cleaned_data.get('name') if form.is_valid() else request.POST.get('name')
        
        # Увеличиваем счетчик запросов, если город существует
        if city_name:
            city, created = City.objects.get_or_create(name=city_name)
            city.request_count += 1
            city.save()

    form = CityForm()  # Очищаем форму

    for city in cities:
        try:
            weather_response = requests.get(url=url.format(city=city.name, api_key=api_key))
            weather_response.raise_for_status()
            weather_json = weather_response.json()
            if 'current' in weather_json:
                city_info = {
                    'city': city.name,
                    'temp': weather_json['current']['temp_c'],
                    'icon': weather_json['current']['condition']['icon'],
                    'requests': city.request_count
                }
            else:
                city_info = {
                    'city': city.name,
                    'temp': 'N/A',
                    'icon': 'N/A'
                }
        except requests.exceptions.RequestException as _ex:
            error_message = f"Произошла ошибка: {_ex}"
            city_info = {
                'city': city.name,
                'temp': 'N/A',
                'icon': 'N/A'
            }

        all_cities.append(city_info)

    return render(
        request=request,
        template_name='weather/index.html',
        context={
            'all_info': all_cities,
            'form': form,
            'error_message': error_message
        },
    )
