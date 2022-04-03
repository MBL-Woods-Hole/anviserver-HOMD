import os,sys
import re
import shutil
import argparse
import datetime
import zipfile
import io

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, User
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.shortcuts import render
#from django.http import JsonResponse, Http404
from django.http import Http404, JsonResponse, HttpResponse
from django.conf import settings
from main.models import Project, Team, TeamUser, ProjectTeam, ProjectLink
from main.utils import get_pangenome

from anvio import dbops
from anvio.tables import miscdata, collections
from anvio.utils import get_TAB_delimited_file_as_dictionary

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

def list_pangenomes(request):
    #action = request.POST.get('action')
    #testObj = [{'name':'Prochlorococcus'},{'name':'other'}]
    #import glob
    #read dir settings.PANGENOME_DATA_DIR
    pgobj=[]
    lst = os.listdir(settings.PANGENOME_DATA_DIR)
    for d in lst:  # use the dirname as pg name
        obj = {'name':d}
        #pfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'PAN.db')
        #if len(pfile) > 0:
        #panfile = os.path.basename(pfile[0]) # take only the first one
        obj['panfile'] = 'PAN.db' #pfile
        
        #gfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'GENOMES.db')
        #genomesfile = os.path.basename(gfile[0])
        obj['genomesfile'] =  'GENOMES.db' #gfile
        
        #dfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'description.txt')
        #descfile = os.path.basename(dfile[0])
        obj['description'] =  read_file(request, os.path.join(settings.PANGENOME_DATA_DIR, d,'description.txt')) #'description.txt' #dfile
        obj['path'] =   os.path.join(settings.PANGENOME_DATA_DIR, d)
        pgobj.append(obj)
        
    
    context = {
       # 'pangenomes': Pangenome.objects,
        'pangenomes': pgobj
    }
    return render(request, 'pangenomes/list.html', context)

def read_file(request, file_path):
    f = open(file_path, 'r')
    file_content = f.read()
    f.close()
    #context = {'file_content': file_content}
    return file_content

def download_pangenome_zip(request, pangenome):
    pangenome = get_pangenome(pangenome)
    logger.debug('in download_pangenome_zip')
    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for f in os.listdir(os.path.join(settings.PANGENOME_DATA_DIR, pangenome.name)):
            backup_zip.write(os.path.join(settings.PANGENOME_DATA_DIR, pangenome.name, f), f)

    response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=HOMD_pangenome_%s' % pangenome.name + ".zip"
    response['Content-Length'] = zip_io.tell()
    return response

def details_pangenome(request, pangenome_name):
    pangenome = get_pangenome( pangenome_name)

    files = []
    for f in os.listdir(pangenome.get_path()):
        files.append({'name': f, 'size': os.path.getsize(os.path.join(pangenome.get_path(), f))})

    context = {
        'pangenome': pangenome,
        'pangenome_files': files
    }
    return render(request, 'pangenomes/details.html', context)