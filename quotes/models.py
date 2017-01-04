from django.db import models
import datetime
from django.utils import timezone

# Create your models here.


class Author(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.name

class Quote(models.Model):
	quote_text = models.CharField(max_length=420)
	pub_date = models.DateTimeField('date published')
	votes = models.IntegerField(default=0)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)

	def __str__(self):
		return self.quote_text

	def was_published_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=1) <= self.pub_date <= now

	class Meta:
		unique_together = (("quote_text", "author"),)