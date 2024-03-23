from django import forms

class StepForm(forms.Form):
    Step = forms.ChoiceField(choices=[(0.0025, 0.0025), (0.005, 0.005), (0.01, 0.01)])
