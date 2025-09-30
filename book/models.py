from django.db import models
from .consts import MAX_RATE

RATE_CHOICES = [(x, str(x)) for x in range(0, MAX_RATE + 1)]

# Create your models here.

# #モデル（DB）の名前をクラスとして定義
# Class SampleModel(models.Model):
# #データを呼び出すときに使う名前。
#     title = models.CharField(max_length=100)
#     number = models.IntegerField()

CATEGORY = (('technical', '技術書'), ('novel', '小説'), ('magazine', '雑誌'), ('law', '法律'),('comics', 'コミック'),('business', 'ビジネス'),('qualification', '資格'),('other', 'その他'))

class Book(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    thumbnail = models.ImageField(null=True, blank=True)
    category = models.CharField(
        max_length=100,
        choices= CATEGORY
    )

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    rate = models.IntegerField(choices = RATE_CHOICES)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title