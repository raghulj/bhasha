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
from django.core.servers.basehttp import FileWrapper


from projects.models import Project
from projects.models import Catalogue
from projects.models import Language
from projects.models import Translation

import datetime
from datetime import date
import uuid

from forms import DocumentForm
from djutils.decorators import async
import xml.etree.ElementTree as ET
import cStringIO as StringIO
import os
import tempfile
import zipfile


def home(request):
    ctx = RequestContext(request, {})
    projects = Project.objects.all()
    return render_to_response("projects/index.html", {'projects': projects}, context_instance=ctx)


def list_languages(request, project_id):
    ctx = RequestContext(request, {})
    project = Project.objects.get(id=project_id)
    languages = Language.objects.filter(project=project)
    return render_to_response("projects/languages.html", {'languages': languages, 'project': project}, context_instance=ctx)


def translations(request, project_id, language_id):
    ctx = RequestContext(request, {})
    project = Project.objects.get(id=project_id)
    language = Language.objects.get(id=language_id)
    if request.method == 'POST':

        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            input_file = request.FILES['docfile']
            persist_uploaded_file(project, request.POST['language'], request.POST['platform'], input_file)

        return render_to_response('translations/index.html', {'project': project, 'language': language, 'form': form}, context_instance=ctx)
    else:
        form = DocumentForm()
        return render_to_response('translations/index.html', {'project': project, 'language': language, 'form': form}, context_instance=ctx)


## based on the type of file extract the key and values to the respective database file
def persist_uploaded_file(project, uploaded_language_id, platform, doc_data):
    if platform == "android":
        doc_data = doc_data.read()
        doc_data = doc_data.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
        parse_android_xml(doc_data, project)
    else:
        lines = doc_data.readlines()
        for line in lines:
            key, value = get_strings(line)
            print key
            if key:
                persist(key, value, project)

    ## initialize or update the respective table with empty or new values
    init_language(project, uploaded_language_id, platform)


## update the catalogue with the last file uploaded
def persist(key, value, project):

    try:
        catalogue = Catalogue.objects.get(msg_key=key)
    except Catalogue.DoesNotExist:
        print  "New value " + value
        catalogue = Catalogue()

    catalogue.project = project
    catalogue.msg_key = key
    if value:
        catalogue.description = value
    else:
        catalogue.description = ""

    catalogue.save()
    return catalogue

## Parse android strings.xml file and persist the keys and values in database


def parse_android_xml(doc_data, project):
    resources = ET.fromstring(doc_data)

    for string in resources:
        key = string.attrib["name"]
        value = string.text
        print key
        if key:
            if value == None:
                value = ""
            persist(key, value, project)


#@async
def init_language(project, uploaded_language_id, platform):
    catalogues = Catalogue.objects.filter(project=project)
    languages = Language.objects.filter(project=project)
    for catalogue in catalogues:
        for language in languages:
            try:
                translation = Translation.objects.filter(catalogue=catalogue).get(language=language)
            except Translation.DoesNotExist:
                translation = Translation()

            translation.language = language
            translation.catalogue = catalogue
            translation.project = project

            if str(language.id) == uploaded_language_id:
                print translation.msg_string + " -- " + catalogue.description
                translation.msg_string = catalogue.description
            else:
                if translation.msg_string == "":
                    translation.msg_string = ""
                else:
                    translation.msg_string = translation.msg_string

            translation.save()


def catalogue(request, project_id):
    ctx = RequestContext(request, {})
    project = Project.objects.get(id=project_id)
    languages = Language.objects.filter(project=project)
    catalogue = Catalogue.objects.filter(project=project)
    form = DocumentForm()

    return render_to_response('catalogue/index.html', {'project': project, 'languages': languages, 'form': form, 'catalogue': catalogue}, context_instance=ctx)


def list_catalogue(request, project_id, language_id):
    ctx = RequestContext(request, {})
    project = Project.objects.get(id=project_id)
    language = Language.objects.get(id=language_id)
    translations = Translation.objects.filter(language=language).filter(project=project)
    form = DocumentForm()
    if request.method == "POST":
        msgs = []
        for translation in translations:
            msgs.append(translation.get_data())

        data = {'msgs': msgs, 'project': project.id}
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
    data = {'project': project.id, "msg": translate.get_data()}
    return JsonResponse(data)


def create_catalogue(request, project_id):
    project = Project.objects.get(id=project_id)
    languages = Language.objects.filter(project=project)

    language_id = request.POST['language_id']
    msg_key = request.POST['msg_key']
    msg_string = request.POST['msg_string']

    catalogue = persist(msg_key, msg_string, project)

    if catalogue:
        for language in languages:
            translation = Translation.objects.filter(catalogue=catalogue).filter(language=language)

            if translation.count() == 0:
                translation = Translation()
            else:
                translation = translation[0]

            translation.language = language
            translation.catalogue = catalogue
            translation.project = project

            if str(language.id) == language_id:
                translation.msg_string = catalogue.description
            else:
                if translation.msg_string == "":
                    translation.msg_string = ""
                else:
                    translation.msg_string = translation.msg_string

            translation.save()

        data = {'success': "ok", "catalogue": catalogue.get_data()}
        return JsonResponse(data)
    else:
        data = {'success': "fail", "msg": "Error in saving catalogue"}
        return JsonResponse(data)


def download_translation(request, project_id, language_id):
    platform = request.GET["platform"]
    project = Project.objects.filter(id=project_id)
    language = Language.objects.filter(id=language_id)
    translations = Translation.objects.filter(project=project).filter(language=language)

    if platform == "android":
        strings = generate_android_strings_xml(translations)
    else:
        strings = "empty"

    temp = file("/tmp/strings.xml", "w")
    temp.write(strings.encode('utf-8'))
    temp.close()
    filename = "/tmp/strings.xml"  # Select your file here.
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=strings.xml'
    response['Content-Length'] = os.path.getsize(filename)
    return response


def generate_android_strings_xml(translations_list):
    xml_strings = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml_strings += "<resources>\n"
    for translation in translations_list:
        value = translation.msg_string.replace("&", "&amp;")
        xml_strings += '\t<string name="' + translation.catalogue.msg_key + '">' + value + '</string>\n'
    xml_strings += "</resources>"
    return xml_strings


## apple.strings
def get_strings(line):
    if line:
        try:
            old_key, new_key = line.split("=")

            ## replace the values with ios specific stuff to android xml
            new_key = new_key.split("\n")[0]
            new_key = new_key.replace('"', '').split(';')[0]
            # new_key = new_key.replace("&","&amp;")
            # new_key = new_key.replace("%@","%s")

            ## replace / in keys with _ for xml
            # old_key = old_key.replace("/", "_")
            # old_key = old_key.replace(".", "_")
            # old_key = old_key.strip()
            # old_key = old_key.replace(" ", "_")
            old_key = old_key.replace("\"", "")

            return old_key.strip(), new_key.strip()

        except Exception, e:
            return None, None
