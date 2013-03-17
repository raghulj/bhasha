import simplejson as json
import datetime

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.datastructures import SortedDict
from django.views.decorators.cache import cache_control

from tokenapi.http import JsonResponse, JsonError


from projects.models import Project
from projects.models import Catalogue
from projects.models import Language
from projects.models import Translation

import datetime
from datetime import date
import uuid

from forms import DocumentForm
from djutils.decorators import async



def home(request):
	ctx = RequestContext(request, {})
	projects = Project.objects.all()
	return render_to_response("projects/index.html",{'projects':projects}, context_instance = ctx) 

def list_languages(request,project_id):
	ctx = RequestContext(request, {})
	project = Project.objects.get(id=project_id)
	languages = Language.objects.filter(project=project)
	return render_to_response("projects/languages.html",{'languages':languages, 'project':project}, context_instance = ctx) 


def translations(request,project_id, language_id):
	ctx = RequestContext(request, {})
	project = Project.objects.get(id=project_id)
	language = Language.objects.get(id=language_id)
	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			input_file = request.FILES['docfile']
			lines = input_file.readlines()
			for line in lines:
				key, value = get_strings(line)
				if key:
					catalogue = Catalogue.objects.filter(msg_key=key)
					if catalogue.count() == 0:
						catalogue = Catalogue()
					else:
						catalogue = catalogue[0]

					catalogue.project =project
					catalogue.msg_key = key
					catalogue.description = value
					catalogue.save()

			init_language(project)


		return render_to_response('translations/index.html', {'project': project, 'language': language, 'form': form}, context_instance=ctx )
	else:
		form = DocumentForm()
		print language.id
		return render_to_response('translations/index.html', {'project': project, 'language': language, 'form': form}, context_instance=ctx )


@async
def init_language(project):

	catalogues = Catalogue.objects.filter(project=project)
	languages = Language.objects.filter(project=project)
	for catalogue in catalogues:
		for language in languages:
			translation = Translation.objects.filter(catalogue=catalogue).filter(language=language)
			if translation.count() == 0:
				print "creating new value for "+catalogue.msg_key
				translation = Translation()
				translation.language = language
				translation.catalogue = catalogue
				translation.project = project
				translation.msg_string = ""
				translation.save()

def catalogue(request,project_id):
	ctx = RequestContext(request, {})
	project = Project.objects.get(id=project_id)
	languages = Language.objects.filter(project=project)
	catalogue = Catalogue.objects.filter(project=project)
	form = DocumentForm()

	return render_to_response('catalogue/index.html', {'project': project, 'languages': languages, 'form': form, 'catalogue':catalogue}, context_instance=ctx )

def list_catalogue(request,project_id,language_id):
	ctx = RequestContext(request, {})
	project = Project.objects.get(id=project_id)
	language = Language.objects.get(id=language_id)
	translations = Translation.objects.filter(language=language).filter(project=project)
	form = DocumentForm()
	if request.method == "POST":	
		msgs = []	
		for translation in translations:
			msgs.append(translation.get_data())

		data = {'msgs':msgs,'project':project.id}
		return JsonResponse(data)	
	else:
		return JsonError("Only GET is allowed")

def update_translations(request, project_id, language_id):
	ctx = RequestContext(request, {})
	project = Project.objects.get(id=project_id)
	language = Language.objects.filter(id=language_id)
	translate = Translation.objects.get(id=request.POST["translation_id"])
	translate.msg_string = request.POST["msgstr"]
	translate.save()
	data = {'project':project.id, "msg":translate.get_data()}
	return JsonResponse(data)




## apple.strings
def get_strings(line):	
	if line:
		try:
			old_key, new_key = line.split("=")

			## replace the values with ios specific stuff to android xml 
			new_key = new_key.split("\n")[0]
			new_key = new_key.replace('"','').split(';')[0]
			# new_key = new_key.replace("&","&amp;")
			# new_key = new_key.replace("%@","%s")

			## replace / in keys with _ for xml
			# old_key = old_key.replace("/", "_")
			# old_key = old_key.replace(".", "_")
			# old_key = old_key.strip()
			# old_key = old_key.replace(" ", "_")
			old_key = old_key.replace("\"","")

			return old_key.strip(),new_key.strip()

		except Exception, e:
			return None,None