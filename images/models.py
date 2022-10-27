from django.conf import settings
from django.db import models
from django.utils.text import slugify

# Create your models here.
class Images(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='images_created', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    sulg = models.SlugField(max_length=200, blank=True)
    url = models.URLField()
    images = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True, db_index=True)
    users_link = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='images_linkd', blank=True)


    def __str__(self):
        return self.title
    

    def save(self, *args, **kwargs):
        if not self.sulg:
            self.sulg = slugify(self.title)
        super().save(*args, **kwargs)