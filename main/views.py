from django.shortcuts import render
import json
from assets.scoring import get_actual_crimininal_data
from main.forms import StepForm
from django.conf import settings

def main_view(request):
    form = StepForm(request.POST or None)
    # default step = 1
    step = 0.01
    if request.method == 'POST' and form.is_valid():
        step = float(form.cleaned_data['Step'])

    data_new = get_actual_crimininal_data(step)
    data_new = {str(key): value for key, value in data_new.items()}
    data_new = json.dumps(data_new)
    print('data_new:', data_new)
    return render(request, 'main_page.html', {'form': form, 'data': data_new, 'step': step, 'google_map_api_key': settings.GOOGLE_MAP_API_KEY})
