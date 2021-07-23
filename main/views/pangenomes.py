import os,sys
import re
import shutil
import argparse
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, User
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.conf import settings
from main.models import Project, Team, TeamUser, ProjectTeam, ProjectLink
from main.utils import get_pangenome_files

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
    import glob
    #read dir settings.PANGENOME_DATA_DIR
    pgobj=[]
    lst = os.listdir(settings.PANGENOME_DATA_DIR)
    for d in lst:  # use the dirname as pg name
        obj = {'name':d}
        pfile = glob.glob(os.path.join(settings.PANGENOME_DATA_DIR,d)+'/*PAN.db')
        #if len(pfile) > 0:
        panfile = os.path.basename(pfile[0]) # take only the first one
        obj['panfile'] = panfile
        gfile = glob.glob(os.path.join(settings.PANGENOME_DATA_DIR,d)+'/*GENOMES.db')
        #if len(gfile) > 0:
        genomesfile = os.path.basename(gfile[0])
        obj['genomesfile'] =  genomesfile
        #if 'panfile' in obj and 'genomesfile' in obj:
        pgobj.append(obj)
        
    
    context = {
       # 'pangenomes': Pangenome.objects,
        'pangenomes': pgobj
    }
    return render(request, 'pangenomes/list.html', context)


def details_pangenome(request, pangenome_name):
    pangenome = get_pangenome_files( pangenome_name)

    files = []
    for f in os.listdir(pangenome.get_path()):
        files.append({'name': f, 'size': os.path.getsize(os.path.join(pangenome.get_path(), f))})

    context = {
        'pangenome': pangenome,
        'pangenome_files': files
    }
    return render(request, 'pangenomes/details.html', context)