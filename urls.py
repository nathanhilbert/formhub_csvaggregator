# app specific urls

from django.conf.urls.defaults import *


urlpatterns = patterns('tamisexport.views',
    url(r'^$', 'tamisexport', name='tamisexport'),
    url(r'^createconnection$', 'tamisexport_create', name='tamisexport_create'),
    url(r'^api/(?P<id>[^/]*)$', 'tamisexport_api', name="tamisexport_api"),
    #url(r'^refreshall$', 'tamisexport_checkrefresh', name="tamisexport_checkrefresh"),
    url(r'^(?P<id>[^/]*)$', 'tamisexport_details', name="tamisexport_details"),
    url(r'^(?P<id>[^/]*)/edit$', 'tamisexport_edit', name="tamisexport_edit"),
    url(r'^(?P<id>[^/]*)/refresh$', 'tamisexport_refresh', name="tamisexport_refresh"),

    #url(r'^(?P<id>[^/]*)/delete$', 'tamisexport_delete', name="tamisexport_delete"),
    #url(r'^html$', 'search_page', {'template': 'search/search_content.html'}, name='search_content'),
    #url(r'^api$', 'search_api', name='search_api'),
    #url(r'^api/data$', 'search_api', kwargs={'type':'layer'}, name='layer_search_api'),
    #url(r'^api/maps$', 'search_api', kwargs={'type':'map'}, name='maps_search_api'),
    #url(r'^api/documents$', 'search_api', kwargs={'type':'document'}, name='document_search_api'),
    #url(r'^api/authors$', 'author_list', name='search_api_author_list'),
    #url(r'^form/$', 'advanced_search', name='advanced_search'), 
)
