from django import forms

class StepForm(forms.Form):
    Area_Size = forms.ChoiceField(choices=[(1, '0.056 км2'), (2, '0.226 км2'), (3, '0.9 км2')])
