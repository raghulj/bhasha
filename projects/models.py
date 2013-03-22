from django.db import models
from django.contrib import admin
from django.utils.datastructures import SortedDict


class Project(models.Model):
    title = models.CharField(max_length=1000, blank=False)
    detail = models.CharField(max_length=1000, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)

    ## returns the data of the model in dic.
    def get_data(self):
        project_id = SortedDict()
        project_id['id'] = self.id
        project_id['title'] = self.title
        project_id['detail'] = self.detail
        project_id['created_date'] = self.created_date.isoformat()
        project_id['is_published'] = self.is_published
        return project_id

    def __unicode__(self):
        return u'%s' % (self.title)

    class Meta:
        db_table = "projects"


class Catalogue(models.Model):
    fields = ['msg_key', 'description']

    project = models.ForeignKey(Project)
    msg_key = models.CharField(max_length=1000, blank=False)
    description = models.CharField(max_length=1000, blank=True)
    comment = models.CharField(max_length=1000, blank=True)
    is_published = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

    def get_data(self):
        catalogue = SortedDict()
        catalogue['id'] = self.id
        catalogue['msgid'] = self.msg_key
        catalogue['msgstr'] = self.description
        catalogue['comments'] = self.comment
        return catalogue

    def __unicode__(self):
        return u'%s' % (self.msg_key)

    class Meta:
        db_table = "catalogues"


class Language(models.Model):
    project = models.ForeignKey(Project)
    language_id = models.CharField(max_length=20, blank=False)
    description = models.CharField(max_length=50, blank=True)

    def calculatePercentage(self):
        tot = self.translation_set.count()
        per = float(tot - self.translation_set.filter(msg_string="").count()) / float(tot) * 100
        return int(per)

    def __unicode__(self):
        return u'%s' % (self.description)

    percent_complete = property(calculatePercentage)

    class Meta:
        db_table = "languages"


class Translation(models.Model):
    language = models.ForeignKey(Language)
    catalogue = models.ForeignKey(Catalogue)
    project = models.ForeignKey(Project)
    msg_string = models.CharField(max_length=1000, blank=True)
    comments = models.CharField(max_length=1000, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    def get_data(self):
        translate = SortedDict()
        translate['id'] = self.id
        translate['msgid'] = self.catalogue.msg_key
        translate['msgstr'] = self.msg_string
        translate['comments'] = self.catalogue.comment
        return translate

    def __unicode__(self):
        return u'%s' % (self.msg_string)

    class Meta:
        db_table = "translations"

## add to Admin module

admin.site.register(Project)
admin.site.register(Catalogue)
admin.site.register(Language)
admin.site.register(Translation)
