from django.shortcuts import render
import json
from django.db.models import Q
from main.forms import StepForm
from django.conf import settings
from main.models import AreaScoring, Crime
from django.http import JsonResponse
import math
def crime_details(request):
    lat = float(request.GET.get('lat'))
    lon = float(request.GET.get('lon'))
    step = float(request.GET.get('step'))

    step_len = len(str(step).split('.')[1])
    lat = round((math.floor(lat * (1 / step)) * step) + float(step), step_len)
    lon = round(math.floor(lon * (1 / step)) * step, step_len)

    data = Crime.objects.all()
    data = [{'crime_title': row.crime_title, 'date': row.date.strftime('%Y-%m-%d')}
            for row in data
            if round((math.floor(row.latitude * (1 / step)) * step) + float(step), step_len) == lat and
            round(math.floor(row.longitude * (1 / step)) * step, step_len) == lon]

    return JsonResponse({'data': data})
def main_view(request):
    form = StepForm(request.POST or None)
    # default step_id = 1
    step = 1
    if request.method == 'POST' and form.is_valid():
        step = int(form.cleaned_data['Area_Size'])

    scoring = AreaScoring.objects
    scoring = scoring.filter(step_id=step)

    scoring = [{'lon': row.longitude, 'lat': row.latitude, 'score': row.score} for row in scoring]
    step_dict = {1: 0.0025, 2: 0.005, 3: 0.01}
    return render(request, 'map.html', {'form': form, 'data': scoring, 'step': step_dict[step] or 0.01, 'google_map_api_key': settings.GOOGLE_MAP_API_KEY})