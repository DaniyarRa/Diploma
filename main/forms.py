from django import forms

class StepForm(forms.Form):
    Step = forms.ChoiceField(choices=[(1, 0.0025), (2, 0.005), (3, 0.01)])
