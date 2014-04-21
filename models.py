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
from datetime import datetime
import os
import hashlib
from urlparse import urlparse

import httplib2
import urllib
import logging

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.staticfiles.templatetags import staticfiles
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse

from odk_logger.models import XForm
from tamisexport.enumerations import DATAUPDATE_FREQ

import base64
import httplib2
from urllib import urlencode
from google.refine import refine



#from geonode.base.enumerations import ALL_LANGUAGES, \
#    HIERARCHY_LEVELS, UPDATE_FREQUENCIES, \
#    DEFAULT_SUPPLEMENTAL_INFORMATION, LINK_TYPES
#from geonode.utils import bbox_to_wkt
#from geonode.people.models import Profile, Role
#from geonode.security.models import PermissionLevelMixin
#from geonode.datamanager.utils import createLayerFromCSV
from django.utils.timezone import utc
from utils.export_tools import generate_export
from odk_viewer.models import Export


#from taggit.managers import TaggableManager

#logger = logging.getLogger("geonode.datamanger.models")


class TAMISConnection(models.Model):
    

    formid = models.ForeignKey(XForm, blank=True, null=True)

    #userid = models.ForeignKey(User, blank=True, null=True)


    # section 1
    alphanumeric = RegexValidator(r'^[\w\-\s]*$', 'Only alphanumeric characters are allowed.')
    title = models.CharField(_('Data Connection Name'), max_length=255, help_text=_('Title of data connection or survey'), unique=True, validators=[alphanumeric])
    creation_date = models.DateTimeField(_('date'), auto_now_add=True, help_text=_('Time this connection was created')) # passing the method itself, not the result
    lastedit_date = models.DateTimeField(_('date'), auto_now_add=True, help_text=_('Last time this was edited')) 

    description_con = models.TextField(_('Description'), blank=True, help_text=_('Brief narrative summary of the content of the resource(s)'))

    tamis_url = models.URLField(_('Formhub URL'), help_text=_('This should be in the format of https://formhub.org/[user name]/forms/[survey name]'))
    tamis_username = models.CharField(_('Formhub username'), max_length=255, help_text=_('User name of of your formhub account'))
    tamis_password = models.CharField(_('Formhub Password'), max_length=255, help_text=_('Password of FormHub Account'))


    update_freq = models.CharField(_('Update Frequency'), max_length=255, help_text=_('Automatically pull in data from Formhub'))

    tamis_formname = models.CharField(_('TAMIS Form Name'), max_length=255, help_text=_('The Formname to use'))

    openrefine_transformation = models.TextField(_('Transformation Text'), blank=True, help_text=_('The Formname to use'))
    openrefine_projectnumber = models.CharField(_('OpenRefine project Number'), max_length=255, blank=True, null=True, default="", help_text=_('To be used by OpenRefine'))

    def createOR(self):
        refiner = refine.Refine(server="http://localhost:3333")
        fileobject = generate_export(Export.CSV_EXPORT, 'csv', self.formid.user.username, self.formid.id_string,
            export_id=None, filter_query=None, group_delimiter='~',
            split_select_multiples=False)
        #need to replace the n/as of the formhub exports
        tempcontents = ""
        with open(fileobject.full_filepath, 'rb') as thefile:
            tempcontents = thefile.read()
        thefile.close()
        tempcontents = tempcontents.replace("n/a","")
        with open(fileobject.full_filepath, 'wb') as thefile:
            thefile.write(tempcontents)

        refineproj = refiner.new_project(project_file=fileobject.full_filepath,
            project_name=self.title,
            store_blank_rows=True,
            store_blank_cells_as_nulls=True)
        if refineproj.project_id:
            self.openrefine_projectnumber = refineproj.project_id
            self.save()
            return refineproj
        else:
            return None

    def applyOR(self, refineproj):
        if self.openrefine_transformation and self.openrefine_transformation != "":
            import json
            entryobject = json.loads(self.openrefine_transformation)
            operations = []
            print entryobject
            for entry in entryobject['entries']:
                if 'operation' in entry.keys():
                    operations.append(entry['operation'])
            data = {'operations': json.dumps(operations)}
            r = refineproj.do_json("apply-operations", data=data)
            return True
        else:
            return None

    def deleteOR(self, refineproj=None):
        if not refineproj:
            refiner = refine.RefineProject(server="http://localhost:3333", project_id=int(self.openrefine_projectnumber))
        else:
            refiner = refineproj
        refiner.delete()
        self.openrefine_projectnumber = ""
        self.save()
        return True

    def getUpdatedCSV(self, asText=True):
        refineproj = self.createOR()
        self.applyOR(refineproj)
        f = refineproj.export(export_format='csv')
        self.deleteOR(refineproj)
        return f.read()


    def refresh(self):
        from odk_viewer.models import Export
        #create the project
        #apply operations
        content = self.getUpdatedCSV()

        ### Only for dominodev
        auth = base64.encodestring(self.tamis_username + ':' + self.tamis_password)
        headers = {'Authorization' : 'Basic ' + auth}
        http = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
        http.add_credentials(self.tamis_username, self.tamis_password)

        #http = httplib2.Http()
        params = urlencode(dict(body=content, username=self.tamis_username, password=self.tamis_password))
        #params = urlencode(dict(body=content, dummyvar="dummyvar"))
        resp, content = http.request(self.tamis_url, "POST", params, headers=headers)
        #resp, content = http.request(url, "POST", params)
        print resp.status, content

        return


