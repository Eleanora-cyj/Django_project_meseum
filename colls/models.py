from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from taggit.managers import TaggableManager

class Museum(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Culture(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Coll(models.Model):
    coll_id = models.CharField(max_length=32)
    title = models.CharField(
        max_length=128,
        validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
)
    date = models.CharField(max_length=128)
    image = models.TextField()
    description = models.TextField()

    culture = models.ForeignKey('Culture', on_delete=models.SET_NULL,null=True)
    museum = models.ForeignKey('Museum', on_delete=models.CASCADE)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL,null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,null=True)
    artist = models.ForeignKey('Artist', on_delete=models.SET_NULL,null=True)

    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Comment', related_name='comments_owned')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Fav', related_name='favorite_colls')

    def __str__(self):
        return self.title

# class ImageModel(models.Model):
#     img = models.ImageField(upload_to='img/',null=True)
#     coll = models.ForeignKey('Coll', on_delete=models.CASCADE, null=True)
        
class Comment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    coll = models.ForeignKey('Coll', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'

class Fav(models.Model) :
    coll = models.ForeignKey('Coll', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('coll', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.coll.title[:10])
