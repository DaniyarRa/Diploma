from django.shortcuts import render
import json
from assets.scoring import init
from main.forms import StepForm
from django.conf import settings
from main.models import AreaScoring

def main_view(request):
    form = StepForm(request.POST or None)
    # default step_id = 1
    step = 1
    if request.method == 'POST' and form.is_valid():
        step = int(form.cleaned_data['Area_Size'])

    data_new2 = AreaScoring.objects
    data_new2 = data_new2.filter(step_id=step)

    data_new2 = {('(' + str(row.latitude) + ', ' + str(row.longitude) + ')'): row.score for row in data_new2}
    data_new2 = json.dumps(data_new2)
    step_dict = {1: 0.0025, 2: 0.005, 3: 0.01}
    return render(request, 'map.html', {'form': form, 'data': data_new2, 'step': step_dict[step] or 0.01, 'google_map_api_key': settings.GOOGLE_MAP_API_KEY})