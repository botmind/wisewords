from django import forms

class QuoteForm(forms.Form):
	author_name = forms.CharField(label='Author', max_length=100)
	quote_text = forms.CharField(label='Quote', max_length=420, widget=forms.Textarea)
