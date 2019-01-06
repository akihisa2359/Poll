import datetime
from django.db import models
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
		
class Age(models.Model):
    range_list = [
        '0~20', '21~30', '31~40', '41~50', '51~60', '61~'
        ]
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    age_range = models.CharField(max_length=50)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return str(self.votes)