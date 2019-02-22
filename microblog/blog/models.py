from django.db import models

# Create your models here.


class Blog(models.Model):

    content = models.CharField(max_length=140)
    posted_date = models.DateTimeField(auto_now_add=True)
