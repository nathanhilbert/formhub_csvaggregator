# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList

#from geonode.maps.views import default_map_config
#from geonode.maps.models import Layer
#from geonode.maps.models import Map
#from geonode.documents.models import Document
#from geonode.people.models import Profile 
#from geonode.search.search import combined_search_results
#from geonode.search.util import resolve_extension
#from geonode.search.normalizers import apply_normalizers
#from geonode.search.query import query_from_request
#from geonode.search.query import BadQuery
#from geonode.base.models import TopicCategory
#from geonode.datamanager.forms import DataConnectionCreateForm, DataConnectionEditForm
#from geonode.datamanager.models import DataConnection

#from geonode.datamanager.enumerations import ENUMTIMES

from tamisexport.models import TAMISConnection
from tamisexport.forms import TAMISConnectionCreateForm
from tamisexport.tamisutils import testFormhubConnection

from datetime import datetime, timedelta 
from time import time
import json
import cPickle as pickle
import operator
import logging
import zlib


logger = logging.getLogger(__name__)




@login_required
def tamisexport(request, template='tamisexport/datamanager.html', **kw):
    initial_query = request.REQUEST.get('q','')
    dataconnection_objs = TAMISConnection.objects.all()

    return render_to_response(template, RequestContext(request, {"object_list":dataconnection_objs}))

@login_required
def tamisexport_create(request, template='tamisexport/dataconnection_create.html'):


    if request.method == "POST":
        dataconnection_form = TAMISConnectionCreateForm(request.POST)

    else:
        dataconnection_form = TAMISConnectionCreateForm()
    print dataconnection_form
    if request.method == "POST" and dataconnection_form.is_valid():
        validformcon, msg = testFormhubConnection(dataconnection_form.cleaned_data['tamis_url'], 
                                    dataconnection_form.cleaned_data['tamis_username'],
                                    dataconnection_form.cleaned_data['tamis_password'])
        if not validformcon:
            errors = dataconnection_form._errors.setdefault("tamis_url", ErrorList())
            errors.append(msg)
        else:
            dataconnection = dataconnection_form.save()
            #redirect
            #return HttpResponseRedirect(reverse('/datamanager/' + str(dataconnection.id) + '/edit'))#, args=(layer.typename,)))
            return HttpResponseRedirect(reverse('tamisexport'))



    # if request.method == "POST" and layer_form.is_valid():
    #     new_poc = layer_form.cleaned_data['poc']
    #     new_author = layer_form.cleaned_data['metadata_author']
    #     new_keywords = layer_form.cleaned_data['keywords']


    return render_to_response(template, RequestContext(request, {
        "dataconnection_form": dataconnection_form,
    }))


@login_required
def tamisexport_edit(request, id, template='tamisexport/dataconnection_create.html'):

    #double check dataconnection
    dataconnection = TAMISConnection.objects.get(id=int(id))


    if request.method == "POST":
        dataconnection_form = TAMISConnectionCreateForm(request.POST, instance=dataconnection, TAMISConnection=dataconnection)

    else:
        dataconnection_form = TAMISConnectionCreateForm(instance=dataconnection, TAMISConnection=dataconnection)

    if request.method == "POST" and dataconnection_form.is_valid():
        dataconnection = dataconnection_form.save()
        #dataconnection.refresh()
        #redirect to layer
        return HttpResponseRedirect(reverse('tamisexport'))#, args=(layer.typename,)))



    # if request.method == "POST" and layer_form.is_valid():
    #     new_poc = layer_form.cleaned_data['poc']
    #     new_author = layer_form.cleaned_data['metadata_author']
    #     new_keywords = layer_form.cleaned_data['keywords']


    return render_to_response(template, RequestContext(request, {
        "dataconnection": dataconnection,
        "dataconnection_form": dataconnection_form,
    }))

@login_required
def tamisexport_refresh(request, id, template='tamisexport/dataconnection_create.html'):
    dataconnection = TAMISConnection.objects.get(id=int(id))
    dataconnection.refresh()
    return HttpResponseRedirect(reverse('tamisexport_details', args=(dataconnection.id,)))


@login_required
def tamisexport_details(request, id, template='tamisexport/dataconnection_details.html'):
    dataconnection = TAMISConnection.objects.get(id=int(id))

    return render_to_response(template, RequestContext(request, {"dataconnection":dataconnection, "layerurl": None}))

# @login_required
# def dataconnection_delete(request, id, template='datamanager/dataconnection_confirm_delete.html'):
#     #double check dataconnection
#     dataconnection = DataConnection.objects.get(id=int(id))


#     confirm = request.GET.get('confirm', None)
#     cancel = request.GET.get('cancel', None)
#     if confirm == "Confirm":
#         dataconnection.delete()
#         return HttpResponseRedirect(reverse('datamanager'))
#     elif cancel == "Cancel":
#         return HttpResponseRedirect(reverse('dataconnection_details', args=(dataconnection.id,)))

#     return render_to_response(template, RequestContext(request, {
#         "dataconnection": dataconnection,
#     }))

# from django.utils.timezone import utc

# #login_required
# def dataconnection_checkrefresh(request, template=None):
#     dataconnections = DataConnection.objects.all()
#     for dataconnection in dataconnections:
#         checkint = (ENUMTIMES[dataconnection.update_freq]) if dataconnection.update_freq else 0
#         if checkint < 1:
#             continue
#         currenttime = datetime.now()
#         future = dataconnection.lastedit_date + timedelta(seconds=checkint)
#         if future < currenttime:
#             dataconnection.refresh()
#     return HttpResponseRedirect(reverse('datamanager'))

