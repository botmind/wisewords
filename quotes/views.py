from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from .models import Quote, Author
from .forms import QuoteForm

# Create your views here.
def index(request):
	last_five_quotes = Quote.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
	context = {
		'last_five_quotes': last_five_quotes
	}	
	return render(request, 'quotes/index.html', context)

def quote_detail(request, quote_id):
	#if quote's pub date is in the future, return 404
	quote = get_object_or_404(Quote, pub_date__lte=timezone.now(), pk=quote_id)
	return render(request, 'quotes/detail.html', {'quote': quote})

def author_quotes(request, author_id):
	author = get_object_or_404(Author, pk=author_id)
	quotes = author.quote_set.filter(pub_date__lte=timezone.now())
	return render(request, 'quotes/author.html', {'quotes': quotes, 'author': author})

def vote(request, quote_id):
	quote = get_object_or_404(Quote, pk=quote_id)
	quote.votes += 1
	quote.save()
	return HttpResponseRedirect(reverse('quotes:quote_detail', args=(quote_id,)))

def new_quote(request):
	if request.method == 'POST':
		# create form instance and populate with data from request
		form = QuoteForm(request.POST)
		if form.is_valid():
			#process data in form.cleaned_data
			author_name = form.cleaned_data['author_name']
			quote_text = form.cleaned_data['quote_text']
			pub_date = timezone.now()

			try:
				author = Author.objects.get(name=author_name)
			except Author.DoesNotExist:
				author = Author(name=author_name)
				author.save()
			
			quote_exists = Quote.objects.filter(quote_text=quote_text, author=author)

			if not quote_exists:
				quote = Quote(author=author, quote_text=quote_text, pub_date=pub_date)
				quote.save()
				#redirect to new URL
				return HttpResponseRedirect(reverse('quotes:index'))
			else:
				form.add_error('quote_text', 'This quote already exists.')
			
	else:
		#if GET, create blank form
		form = QuoteForm()

	return render(request, 'quotes/new_quote.html', {'form': form})
