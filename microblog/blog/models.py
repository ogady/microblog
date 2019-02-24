from django.db import models


# Create your models here.


class Blog(models.Model):
    content = models.CharField(max_length=140)
    photo = models.ImageField(upload_to='anicolleblog', null=True, blank=True)
    posted_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_date']
