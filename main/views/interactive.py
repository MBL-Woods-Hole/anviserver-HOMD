from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from main.utils import get_project, get_pangenome, check_view_permission, check_write_permission
from main.models import Project, Pangenome
from main.templatetags.gravatar import gravatar
import main.utils as utils

from anvio.bottleroutes import BottleApplication
from anvio.argparse import ArgumentParser
import bin.anvi_display_panAV as ADP
import anvio.interactive as interactive

import zipfile
import hashlib
import json
import enum
import os,sys
import io

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

def short_link_redirect(request, short_link_key):
    project = get_object_or_404(Project, short_link_key=short_link_key)

    if not project.is_public:
        raise Http404

    return redirect('show_interactive', username=project.user.username, project_slug=project.slug)


def show_interactive(request, username, project_slug):
    logger.debug('IN show interactive')
    
    
    project = get_project(username, project_slug)
    
    logger.debug('in show interactive -project:')
    logger.debug(project)
    logger.debug('in show interactive -request:')
    logger.debug(request)
    view_key = request.GET.get('view_key')
    
    if view_key is None:
        view_key = "no_view_key"

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    return render(request, 'interactive.html', {'project': project, 'view_key': view_key, 'is_homd_pangenome':False})
    return ''


    
def show_inspect(request, username, project_slug, inspection_type):
    project = get_project(username, project_slug)

    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    html_page = ''
    if inspection_type == 'inspect':
        html_page = 'charts'
    elif inspection_type == 'geneclusters':
        html_page = 'geneclusters'

    return render(request, 'inspect.html', {'project': project, 
                                           'view_key': view_key,
                                           'id': request.GET.get('id'),
                                           'html_page': html_page
                                           })


def download_zip(request, username, project_slug):
    project = get_project(username, project_slug)

    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for f in os.listdir(project.get_path()):
            backup_zip.write(os.path.join(project.get_path(), f), f)

    response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=%s' % project.slug + ".zip"
    response['Content-Length'] = zip_io.tell()
    return response

def show_pangenome_interactive(request, pangenome):
    
    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"
    logger.debug('in show pangenome interactive - view_key: '+view_key)
    logger.debug(request)
   
    return render(request, 'interactive.html', {'pangenome': pangenome,'view_key':view_key, 'is_homd_pangenome':True})
    
def anvi_display_pan_testing(request, pangenome):
    view_key = request.GET.get('view_key')
    
    if view_key is None:
        view_key = "no_view_key"
    logger.debug('in anvi_display_pan_testing ')
    logger.debug(request)
    pan_db           = os.path.join('pangenomes',pangenome,'PAN.db')      #self.get_file_path('PAN.db', self.name)
    genomes_storage   = os.path.join('pangenomes',pangenome,'GENOMES.db') 
    
    av = ADP.Interactive(pan_db, genomes_storage)
    av.run_app()
    ##
    pgobj=[]
    lst = sorted(os.listdir(settings.PANGENOME_DATA_DIR))
    for d in lst:  # use the dirname as pg name
        #logger.debug('LST '+d)
        sum_bytes = 0
        obj = {'name':d,'size':0}
        path = os.path.join(settings.PANGENOME_DATA_DIR, d)
        obj['path'] = path
        #pfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'PAN.db')
        #if len(pfile) > 0:
        #panfile = os.path.basename(pfile[0]) # take only the first one
        obj['panfile'] = 'PAN.db' #pfile
        sum_bytes += os.path.getsize(os.path.join(path, obj['panfile']))
        #gfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'GENOMES.db')
        #genomesfile = os.path.basename(gfile[0])
        obj['genomesfile'] =  'GENOMES.db' #gfile
        sum_bytes += os.path.getsize(os.path.join(path, obj['genomesfile']))
        #dfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'description.txt')
        #descfile = os.path.basename(dfile[0])
        try:
            obj['description'] =  read_file(os.path.join(path,'description.txt')) #'description.txt' #dfile
        except:
            obj['description'] = 'No Description Found'
        obj['size'] = round(convert_unit(sum_bytes, SIZE_UNIT.MB),2)
        pgobj.append(obj)
        
    context = {
       # 'pangenomes': Pangenome.objects,
        'pangenomes': pgobj
    }
    return render(request, 'pangenomes/list.html', context)
    #return render(request, 'interactive.html', {'pangenome': pangenome,'view_key':view_key, 'is_homd_pangenome':True})
    
    
    
# def anvi_display_pan2(request, pangenome):
#     logger.debug('IN TEST1 ')
#     print('IN TEST2')
#     pan_db           = os.path.join('pangenomes',pangenome,'PAN.db')      #self.get_file_path('PAN.db', self.name)
#     genomes_storage   = os.path.join('pangenomes',pangenome,'GENOMES.db')  #self.get_file_path('GENOMES.db', self.name)
#     pgobj=[]
#     
#     lst = sorted(os.listdir(settings.PANGENOME_DATA_DIR))
#     for d in lst:  # use the dirname as pg name
#         #logger.debug('LST '+d)
#         sum_bytes = 0
#         obj = {'name':d,'size':0}
#         path = os.path.join(settings.PANGENOME_DATA_DIR, d)
#         obj['path'] = path
#         #pfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'PAN.db')
#         #if len(pfile) > 0:
#         #panfile = os.path.basename(pfile[0]) # take only the first one
#         obj['panfile'] = 'PAN.db' #pfile
#         sum_bytes += os.path.getsize(os.path.join(path, obj['panfile']))
#         #gfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'GENOMES.db')
#         #genomesfile = os.path.basename(gfile[0])
#         obj['genomesfile'] =  'GENOMES.db' #gfile
#         sum_bytes += os.path.getsize(os.path.join(path, obj['genomesfile']))
#         #dfile = os.path.join(settings.PANGENOME_DATA_DIR,d,'description.txt')
#         #descfile = os.path.basename(dfile[0])
#         try:
#             obj['description'] =  read_file(os.path.join(path,'description.txt')) #'description.txt' #dfile
#         except:
#             obj['description'] = 'No Description Found'
#         obj['size'] = round(convert_unit(sum_bytes, SIZE_UNIT.MB),2)
#         pgobj.append(obj)
#         
#     context = {
#        # 'pangenomes': Pangenome.objects,
#         'pangenomes': pgobj
#     }
#     #  nohup /path/to/your/script.sh > /dev/null 2>&1 &
#     #cmd = "anvi-display-panAV -p "+pan_db+" -g "+genomes_storage+" -I "+settings.PAN_IP_ADDRESS
#     params = get_default_display_params()
#     params['pan_db'] = pan_db
#     params['genomes_storage'] = genomes_storage
#     print('params')
#     print(params)
#     s = Struct(**params)  
#     d = interactive.Interactive(s)
#     bottle_request = utils.MockBottleRequest(django_request=request)
#     bottle_response = utils.MockBottleResponse()
#     bottleapp = BottleApplication(d, bottle_request, bottle_response)
#     return  JsonResponse(params)
#     #run_pangenome(request, pan_db, genomes_storage)
#     #I.run()
#     #print('RUNNING: '+cmd)
#     #os.system(cmd+" &")
#     #subprocess.Popen("anvi-display-pan -p "+pan_db+" -g "+genomes_storage+" -I localhost -P 8022")
#     
#     return render(request, 'pangenomes/list.html', context)
    
def get_default_display_params():
    # __description__ = "Start an anvi'o server to display a pan-genome"
    """ Trying to replicate anvi-display-pan default arguments. """
    obj = {
       'mode':'pan',
      'additional_layers':None, 
      'additional_view':None, 
      'browser_path':None, 
      'collection_autoload':None, 
      'dry_run':False, 
      'export_svg':None, 
      'ip_address':'localhost', 
      'password_protected':False, 
      'port_number':0, 
      'read_only':False, 
      'server_only':False, 
      'skip_auto_ordering':False, 
      'skip_init_functions':False, 
      'skip_news':False, 
      'state_autoload':None, 
      'title':None, 
      'tree':None, 
      'user_server_shutdown':False, 
      'view':None, 
      'view_data':None
      }
    return obj
    
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
        
class SIZE_UNIT(enum.Enum):
   BYTES = 1
   KB = 2
   MB = 3
   GB = 4
def convert_unit(size_in_bytes, unit):
   """ Convert the size from bytes to other units like KB, MB or GB"""
   if unit == SIZE_UNIT.KB:
       return size_in_bytes/1024
   elif unit == SIZE_UNIT.MB:
       return size_in_bytes/(1024*1024)
   elif unit == SIZE_UNIT.GB:
       return size_in_bytes/(1024*1024*1024)
   else:
       return size_in_bytes
       
def read_file(file_path):
    f = open(file_path, 'r')
    file_content = f.read()
    f.close()
    #context = {'file_content': file_content}
    return file_content 
    
# def ajax_handler_pangenome2(request, pangenome_slug, view_key, requested_url):
#     logger.debug('in interactive.py ajax_handler_pangenome2')
#     
#     pan_db           = os.path.join('pangenomes',pangenome_slug,'PAN.db')      #self.get_file_path('PAN.db', self.name)
#     genomes_storage   = os.path.join('pangenomes',pangenome_slug,'GENOMES.db')  #self.get_file_path('GENOMES.db', self.name)
#     params = get_default_display_params()
#     params['pan_db'] = pan_db
#     params['genomes_storage'] = genomes_storage
#     print('params')
#     print(params)
#     s = Struct(**params)  
#     d = interactive.Interactive(s)
#     bottle_request = utils.MockBottleRequest(django_request=request)
#     bottle_response = utils.MockBottleResponse()
#     
#     bottleapp = BottleApplication(d, bottle_request, bottle_response)
#     #bottleapp = BottleApplication(d)
#     return  JsonResponse(params, safe=False)
#     #return HttpResponse( content_type='application/json')
    
    
@csrf_exempt
def ajax_handler_pangenome(request, pangenome_slug, view_key, requested_url):
    logger.debug('\nrequested_url: '+requested_url)
    # logger.debug('in interactive.py ajax_handler_pangenome')
#     logger.debug('pangenome slug: '+pangenome_slug) # just name of pangenome
#     logger.debug('view_key '+view_key)
    
    username = 'guest'
    
    if not request.is_ajax():
        raise Http404
    read_only = True
    pangenome_obj = get_pangenome(pangenome_slug)
    logger.debug('pangenome name from Class:: '+pangenome_obj.name)
    
    bottle_request = utils.MockBottleRequest(django_request=request)
    bottle_response = utils.MockBottleResponse()
    
    interactive = None
    
    #if not requested_url.endswith('data/news'):
    #    interactive = pangenome_obj.get_interactive(read_only=read_only)
    
    
    args = get_default_display_params()
    args['pan_db']            = os.path.join('pangenomes',pangenome_slug,'PAN.db')      #self.get_file_path('PAN.db', self.name)
    args['genomes_storage']   = os.path.join('pangenomes',pangenome_slug,'GENOMES.db')  #self.get_file_path('GENOMES.db', self.name)
    s = Struct(**args) 
    if not requested_url.endswith('data/news'):
        interactive = pangenome_obj.get_interactive()  #interactive.Interactive(s)
    
    bottleapp = BottleApplication(interactive, bottle_request, bottle_response)
    
    #bottleapp.run_application('localhost', args.port_number)
    
    if requested_url.find('data/init') != -1:
        #logger.debug('caught data/init')
        download_zip_url = reverse('download_zip', args=[username, pangenome_slug])
        if view_key != 'no_view_key':
            download_zip_url += '?view_key=' + view_key

        default_view = interactive.default_view
        default_order = interactive.p_meta['default_item_order']
        autodraw = False
        state_dict = None

        if interactive.state_autoload:
            state_dict = json.loads(interactive.states_table.states[interactive.state_autoload]['content'])

            if state_dict['current-view'] in interactive.views:
                default_view = state_dict['current-view']

            if state_dict['order-by'] in interactive.p_meta['item_orders']:
                default_order = state_dict['order-by']

            autodraw = True

        collection_dict = None
        if interactive.collection_autoload:
            collection_dict = json.loads(bottleapp.get_collection_dict(interactive.collection_autoload))

        functions_sources = []
        if interactive.mode == 'full' or interactive.mode == 'gene':
            functions_sources = list(interactive.gene_function_call_sources)
        elif interactive.mode == 'pan':
            functions_sources = list(interactive.gene_clusters_function_sources)
        obj2 = { 
         "title": pangenome_obj.name,
         "description": interactive.p_meta['description'],
         "item_orders": (default_order, interactive.p_meta['item_orders'][default_order], list(interactive.p_meta['item_orders'].keys())),
         "views": (default_view, interactive.views[default_view], list(interactive.views.keys())),
         "item_lengths": dict([tuple((c, interactive.splits_basic_info[c]['length']),) for c in interactive.splits_basic_info]),
         "server_mode": False,
         "mode": interactive.mode,
         "read_only": interactive.read_only, 
         "bin_prefix": "Bin_",
         "session_id": 0,
         "layers_order": interactive.layers_order_data_dict,
         "layers_information": interactive.layers_additional_data_dict,
         "layers_information_default_order": interactive.layers_additional_data_keys,
         "check_background_process": False,
         "autodraw": autodraw,
         "inspection_available": interactive.auxiliary_profile_data_available,
         "sequences_available": True if interactive.split_sequences else False,
         "functions_initialized": interactive.gene_function_calls_initiated,
         "functions_sources": functions_sources,
         "state": (interactive.state_autoload, state_dict),
         "collection": collection_dict,
         "samples": interactive.p_meta['samples'] if interactive.mode in ['full', 'refine'] else [],
         "load_full_state": True,
         "project": {
             'username': 'guest',
              'download_zip_url': ''  #download_zip_url
             }
        }
        return JsonResponse(obj2)
        
        
        
    elif requested_url.find('data/view/') != -1:
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_view_data(param), content_type='application/json')

    elif requested_url.find('tree/') != -1:
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_items_order(param), content_type='application/json')

    elif requested_url.find('data/collections') != -1:
        return HttpResponse(bottleapp.get_collections(), content_type='application/json')

    elif requested_url.find('data/collection/') != -1:
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_collection_dict(param), content_type='application/json')

    elif requested_url.find('store_collection') != -1:
        if not check_write_permission(pangenome_obj, request.user):
            raise Http404

        ret = HttpResponse(bottleapp.store_collections_dict(), content_type='application/json')
        project.synchronize_num_collections(save=True)
        return ret
########### ADDED ###########################################
    elif requested_url.endswith('data/search_functions'):
        #logger.debug('got search fxn')
        return HttpResponse(bottleapp.search_functions(), content_type='application/json')
    elif requested_url.endswith('data/news'):
        #logger.debug('got news fxn')
        return HttpResponse(bottleapp.get_news(), content_type='application/json')
    elif requested_url.endswith('data/check_homogeneity_info'):
        #logger.debug('got check_homogeneity_info fxn')
        return HttpResponse(bottleapp.check_homogeneity_info(), content_type='application/json')
    elif requested_url.endswith('data/filter_gene_clusters'):
        #logger.debug('got filter_gene_clusters fxn')
        return HttpResponse(bottleapp.filter_gene_clusters(), content_type='application/json')
    elif requested_url.endswith('data/save_tree'):
        #logger.debug('got filter_gene_clusters fxn')
        return HttpResponse(bottleapp.save_tree(), content_type='application/json')
###############################################################    
    elif requested_url.find('data/contig') != -1:
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_sequence_for_split(param), content_type='application/json')

    elif requested_url.find('store_description') != -1:
        if not check_write_permission(pangenome_obj, request.user):
            raise Http404

        return HttpResponse(bottleapp.store_description(), content_type='application/json')

    elif requested_url.find('state/all') != -1:
        return HttpResponse(bottleapp.state_all(), content_type='application/json')

    elif requested_url.find('state/get') != -1:
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_state(param), content_type='application/json')

    elif requested_url.find('state/save') != -1:
        if not check_write_permission(pangenome_obj, request.user):
            raise Http404

        param = requested_url.split('/')[-1]
        ret = HttpResponse(bottleapp.save_state(param), content_type='application/json')
        pangenome_obj.synchronize_num_states(save=True)
        return ret

    elif requested_url.find('data/charts') != -1:
        order_name = requested_url.split('/')[-2]
        item_name = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.charts(order_name, item_name), content_type='application/json')

    elif requested_url.find('geneclusters') != -1:
        order_name = requested_url.split('/')[-2]
        item_name = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.inspect_gene_cluster(order_name, item_name), content_type='application/json')

    elif requested_url.find('get_AA_sequences_for_gene_cluster') != -1:
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_AA_sequences_for_gene_cluster(param), content_type='application/json')

   
    elif requested_url.find('data/gene') != -1:
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_sequence_for_gene_call(param), content_type='application/json')

    elif requested_url.endswith('data/completeness'):
        return HttpResponse(bottleapp.completeness(), content_type='application/json')

    elif requested_url.find('reroot_tree') != -1:
        return HttpResponse(bottleapp.reroot_tree(), content_type='application/json')

    logger.debug('**missing url2: '+requested_url)
    #return JsonResponse(obj2)
    raise Http404

# def ajax_handler(request, project_slug, view_key, requested_url):
#     logger.debug('XXXXX '+project_slug)
#     
# def ajax_handler(request, username, project_slug, view_key, requested_url):
#     logger.debug('in interactive.py ajax_handler(NOT PANGENOME)')
#     logger.debug('username '+username)
#     logger.debug('project_slug '+project_slug)
#     logger.debug('requested_url '+requested_url)
#     if not request.is_ajax():
#         raise Http404
# 
#     #project = get_project(username, project_slug)
#     project = get_pangenome(project_slug)
#     logger.debug(project)
#     
# 
#     read_only = True  #not check_write_permission(project, request.user)
# 
#     bottle_request = utils.MockBottleRequest(django_request=request)
#     bottle_response = utils.MockBottleResponse()
# 
#     interactive = None
#     
#     if not requested_url.startswith('data/news'):
#         interactive = project.get_interactive(read_only=read_only)
# 
#     bottleapp = BottleApplication(interactive, bottle_request, bottle_response)
# 
#     if requested_url.startswith('data/init'):
#         download_zip_url = reverse('download_zip', args=[username, project_slug])
#         if view_key != 'no_view_key':
#             download_zip_url += '?view_key=' + view_key
# 
#         default_view = interactive.default_view
#         default_order = interactive.p_meta['default_item_order']
#         autodraw = False
#         state_dict = None
# 
#         if interactive.state_autoload:
#             state_dict = json.loads(interactive.states_table.states[interactive.state_autoload]['content'])
# 
#             if state_dict['current-view'] in interactive.views:
#                 default_view = state_dict['current-view']
# 
#             if state_dict['order-by'] in interactive.p_meta['item_orders']:
#                 default_order = state_dict['order-by']
# 
#             autodraw = True
# 
#         collection_dict = None
#         if interactive.collection_autoload:
#             collection_dict = json.loads(bottleapp.get_collection_dict(interactive.collection_autoload))
# 
#         functions_sources = []
#         if interactive.mode == 'full' or interactive.mode == 'gene':
#             functions_sources = list(interactive.gene_function_call_sources)
#         elif interactive.mode == 'pan':
#             functions_sources = list(interactive.gene_clusters_function_sources)
# 
#         return JsonResponse({ "title": project.name,
#                              "description": interactive.p_meta['description'],
#                              "item_orders": (default_order, interactive.p_meta['item_orders'][default_order], list(interactive.p_meta['item_orders'].keys())),
#                              "views": (default_view, interactive.views[default_view], list(interactive.views.keys())),
#                              "item_lengths": dict([tuple((c, interactive.splits_basic_info[c]['length']),) for c in interactive.splits_basic_info]),
#                              "server_mode": False,
#                              "mode": interactive.mode,
#                              "read_only": interactive.read_only, 
#                              "bin_prefix": "Bin_",
#                              "session_id": 0,
#                              "layers_order": interactive.layers_order_data_dict,
#                              "layers_information": interactive.layers_additional_data_dict,
#                              "layers_information_default_order": interactive.layers_additional_data_keys,
#                              "check_background_process": False,
#                              "autodraw": autodraw,
#                              "inspection_available": interactive.auxiliary_profile_data_available,
#                              "sequences_available": True if interactive.split_sequences else False,
#                              "functions_initialized": interactive.gene_function_calls_initiated,
#                              "functions_sources": functions_sources,
#                              "state": (interactive.state_autoload, state_dict),
#                              "collection": collection_dict,
#                              "samples": interactive.p_meta['samples'] if interactive.mode in ['full', 'refine'] else [],
#                              "load_full_state": True,
#                              "project": {
#                                 'username': project.user.username,
#                                 'fullname': project.user.userprofile.fullname if project.user.userprofile.fullname else project.user.username,
#                                 'user_avatar': gravatar(project.user.email),
#                                 'download_zip_url': download_zip_url
#                                 }
#                             })
# 
#     elif requested_url.startswith('data/view/'):
#         param = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.get_view_data(param), content_type='application/json')
# 
#     elif requested_url.startswith('tree/'):
#         param = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.get_items_order(param), content_type='application/json')
# 
#     elif requested_url.startswith('data/collections'):
#         return HttpResponse(bottleapp.get_collections(), content_type='application/json')
# 
#     elif requested_url.startswith('data/collection/'):
#         param = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.get_collection_dict(param), content_type='application/json')
# 
#     elif requested_url.startswith('store_collection'):
#         if not check_write_permission(project, request.user):
#             raise Http404
# 
#         ret = HttpResponse(bottleapp.store_collections_dict(), content_type='application/json')
#         project.synchronize_num_collections(save=True)
#         return ret
# 
#     elif requested_url.startswith('data/contig/'):
#         param = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.get_sequence_for_split(param), content_type='application/json')
# 
#     elif requested_url.startswith('store_description'):
#         if not check_write_permission(project, request.user):
#             raise Http404
# 
#         return HttpResponse(bottleapp.store_description(), content_type='application/json')
# 
#     elif requested_url.startswith('state/all'):
#         return HttpResponse(bottleapp.state_all(), content_type='application/json')
# 
#     elif requested_url.startswith('state/get'):
#         param = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.get_state(param), content_type='application/json')
# 
#     elif requested_url.startswith('state/save'):
#         if not check_write_permission(project, request.user):
#             raise Http404
# 
#         param = requested_url.split('/')[-1]
#         ret = HttpResponse(bottleapp.save_state(param), content_type='application/json')
#         project.synchronize_num_states(save=True)
#         return ret
# 
#     elif requested_url.startswith('data/charts/'):
#         order_name = requested_url.split('/')[-2]
#         item_name = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.charts(order_name, item_name), content_type='application/json')
# 
#     elif requested_url.startswith('data/geneclusters/'):
#         order_name = requested_url.split('/')[-2]
#         item_name = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.inspect_gene_cluster(order_name, item_name), content_type='application/json')
# 
#     elif requested_url.startswith('data/get_AA_sequences_for_gene_cluster/'):
#         param = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.get_AA_sequences_for_gene_cluster(param), content_type='application/json')
# 
#     elif requested_url.startswith('data/news'):
#         return HttpResponse(bottleapp.get_news(), content_type='application/json')
# 
#     elif requested_url.startswith('data/gene'):
#         param = requested_url.split('/')[-1]
#         return HttpResponse(bottleapp.get_sequence_for_gene_call(param), content_type='application/json')
# 
#     elif requested_url.startswith('data/completeness'):
#         return HttpResponse(bottleapp.completeness(), content_type='application/json')
# 
#     elif requested_url.startswith('data/reroot_tree'):
#         return HttpResponse(bottleapp.reroot_tree(), content_type='application/json')
# 
# 
#     raise Http404

