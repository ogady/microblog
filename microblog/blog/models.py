from django.db import models


# Create your models here.


class Blog(models.Model):
    content = models.CharField(max_length=140)
    photo = models.ImageField(upload_to='anicolleblog', blank=True, null=True)
    anime_id = models.IntegerField(blank=True, null=True)
    anime = models.CharField(max_length=200, blank=True, null=True)
    posted_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_date']
