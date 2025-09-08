from django import forms

class MathQuestionForm(forms.Form):
    question = forms.CharField(
        label='Pergunta de Matemática',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua pergunta de matemática aqui...',
            'rows': 3
        }),
        max_length=500
    )