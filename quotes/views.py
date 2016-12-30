from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from .models import Quote, Author

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