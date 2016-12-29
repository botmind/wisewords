from django.shortcuts import render

from .models import Quote

# Create your views here.
def index(request):
	last_five_quotes = Quote.objects.order_by('-pub_date')[:5]
	context = {
		'last_five_quotes': last_five_quotes
	}	
	return render(request, 'quotes/index.html', context)

def quote_detail(request, quote_id):
	response = "You are looking at the detail of quote %s."
	return HttpResponse(response % quote_id)

def author_quotes(request, author_id):
	response = "You are looking at the quotes for author %s."
	return HttpResponse(response % author_id)

def vote(request, quote_id):
	return HttpResponse("You are voting on quote %s." % quote_id)