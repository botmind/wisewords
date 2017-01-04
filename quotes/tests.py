from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Quote, Author

from django.urls import reverse

#helper methods

def create_quote(author_name, quote_text, days):
	#create a quote at a given time
	time = timezone.now() + datetime.timedelta(days=days)
	author = Author.objects.create(name=author_name)
	return Quote.objects.create(quote_text=quote_text, pub_date=time, author=author)

# Create your tests here.

class QuoteMethodTests(TestCase):

	def test_was_published_recently_with_future_question(self):
		"""
		was_published_recently() should return False for questions
		with pub_date in future
		"""
		time = timezone.now() + datetime.timedelta(days=30)
		future_quote = Quote(pub_date=time)
		self.assertIs(future_quote.was_published_recently(), False)

	def test_was_published_recently_with_old_question(self):
		"""
		was_published_recently() should return False for questions
		with pub_date older than 1 day
		"""
		time = timezone.now() - datetime.timedelta(days=30)
		old_quote = Quote(pub_date=time)
		self.assertIs(old_quote.was_published_recently(), False)

	def test_was_published_recently_with_recent_question(self):
		"""
		was_published_recently() should return True for questions
		with pub_date less than one day in the past
		"""
		time = timezone.now() - datetime.timedelta(hours=1)
		recent_quote = Quote(pub_date=time)
		self.assertIs(recent_quote.was_published_recently(), True)

class QuoteViewTest(TestCase):

	def test_index_view_with_no_quotes(self):
		response = self.client.get(reverse('quotes:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No quotes are available.")
		self.assertQuerysetEqual(response.context['last_five_quotes'], [])

	def test_index_view_with_a_past_quote(self):
		create_quote(author_name="test_author", quote_text="Past quote", days=-30)
		response = self.client.get(reverse('quotes:index'))
		self.assertContains(response, "Past quote")

	def test_index_view_with_a_future_quote(self):
		create_quote(author_name="test_author", quote_text="Future quote", days=30)
		response = self.client.get(reverse('quotes:index'))
		self.assertNotContains(response, "Future quote")

	def test_index_view_with_a_future_and_past_quote(self):
		create_quote(author_name="test_author1", quote_text="Past quote", days=-30)
		create_quote(author_name="test_author2",quote_text="Future quote", days=30)
		response = self.client.get(reverse('quotes:index'))
		self.assertContains(response, "Past quote")
		self.assertNotContains(response, "Future quote")

	def test_index_view_with_two_past_quotes(self):
		create_quote(author_name="test_author1",quote_text="Past quote 1", days=-30)
		create_quote(author_name="test_author2",quote_text="Past quote 2", days=-10)
		response = self.client.get(reverse('quotes:index'))
		self.assertContains(response, "Past quote 1")
		self.assertContains(response, "Past quote 2")

class DetailViewTest(TestCase):

	def test_quotes_with_future_pub_date_should_not_be_retrievable(self):
		future_quote = create_quote(author_name="test_author", quote_text="Future quote", days=30)
		url = reverse('quotes:quote_detail', args=(future_quote.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404) 

	def test_quotes_with_past_pub_date_should_be_retrievable(self):
		past_quote = create_quote(author_name="test_author", quote_text="Past quote", days=-1)
		url = reverse('quotes:quote_detail', args=(past_quote.id,))
		response = self.client.get(url)
		self.assertContains(response, past_quote.quote_text)

class AuthorQuotesViewTest(TestCase):

	def test_quotes_with_future_pub_date_should_not_be_displayed(self):
		future_quote = create_quote(author_name="test_author", quote_text="Future quote", days=30)
		url = reverse('quotes:author_quotes', args=(future_quote.author.id,))
		response = self.client.get(url)
		self.assertNotContains(response, future_quote.quote_text)

	def test_quotes_with_past_pub_date_should_be_displayed(self):
		past_quote = create_quote(author_name="test_author", quote_text="Past quote", days=-5)
		url = reverse('quotes:author_quotes', args=(past_quote.author.id,))
		response = self.client.get(url)
		self.assertContains(response, past_quote.quote_text)

class VoteViewTest(TestCase):

	def test_upvoting_quote_increases_number_of_votes(self):
		past_quote = create_quote(author_name="test_author", quote_text="Past quote", days=-5)
		url = reverse('quotes:vote', args=(past_quote.id,))
		response = self.client.get(url)
		past_quote = Quote.objects.get(pk=past_quote.id) #have to get from db to see if change was registered there; otherwise, the context remains with the local past_quote
		self.assertEqual(past_quote.votes, 1)

class NewQuoteViewTest(TestCase):

	def test_submit_new_quote_redirects_to_index(self):
		url = reverse('quotes:new_quote')
		response = self.client.post(url, {'author_name': 'test_author', 'quote_text': 'test_quote'})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['Location'], reverse('quotes:index'))

	def test_blank_author_and_quote_is_invalid(self):
		url = reverse('quotes:new_quote')
		response = self.client.post(url, {'author_name': '', 'quote_text': ''})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Author.objects.all().count(), 0)
		self.assertEqual(Quote.objects.all().count(), 0)
		self.assertEqual(response.context['form']['author_name'].errors, ['This field is required.'])
		self.assertEqual(response.context['form']['quote_text'].errors, ['This field is required.'])

	def test_blank_author_is_invalid(self):
		url = reverse('quotes:new_quote')
		response = self.client.post(url, {'author_name': '', 'quote_text': 'test_quote'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Author.objects.all().count(), 0)
		self.assertEqual(Quote.objects.all().count(), 0)
		self.assertEqual(response.context['form']['author_name'].errors, ['This field is required.'])
		self.assertEqual(response.context['form']['quote_text'].errors, [])

	def test_blank_quote_is_invalid(self):
		url = reverse('quotes:new_quote')
		response = self.client.post(url, {'author_name': 'test_author', 'quote_text': ''})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Author.objects.all().count(), 0)
		self.assertEqual(Quote.objects.all().count(), 0)
		self.assertEqual(response.context['form']['quote_text'].errors, ['This field is required.'])
		self.assertEqual(response.context['form']['author_name'].errors, [])

	def test_length_requirements_are_enforced(self):
		url = reverse('quotes:new_quote')
		author_name = 'a' * 101
		quote_text = 'q' * 421
		response = self.client.post(url, {'author_name': author_name, 'quote_text': quote_text})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Author.objects.all().count(), 0)
		self.assertEqual(Quote.objects.all().count(), 0)
		self.assertEqual(response.context['form']['author_name'].errors, ['Ensure this value has at most 100 characters (it has 101).'])
		self.assertEqual(response.context['form']['quote_text'].errors, ['Ensure this value has at most 420 characters (it has 421).'])

	def test_duplicate_authors_are_not_created(self):
		author_name = 'test_author'
		author1 = Author.objects.create(name=author_name)
		self.assertEqual(Author.objects.all().count(), 1)
		url = reverse('quotes:new_quote')
		response = self.client.post(url, {'author_name': author_name, 'quote_text': 'test_quote'})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['Location'], reverse('quotes:index'))
		self.assertEqual(Author.objects.all().count(), 1)
		self.assertEqual(Quote.objects.all().count(), 1)

	def test_duplicate_quotes_for_same_author_are_not_created(self):
		author = Author.objects.create(name="test_author")
		url = reverse('quotes:new_quote')
		response = self.client.post(url, {'author_name': 'test_author', 'quote_text': 'test_quote'})
		self.assertEqual(Quote.objects.all().count(), 1)
		response = self.client.post(url, {'author_name': 'test_author', 'quote_text': 'test_quote'})
		self.assertEqual(Quote.objects.all().count(), 1)
		self.assertEqual(response.context['form']['quote_text'].errors, ['This quote already exists.'])





