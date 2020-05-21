try:
    from django.urls import re_path
except ModuleNotFoundError:
    from django.conf.urls import url as re_path
from . import views

from features.registry import registered_models, registered_links
from features.registry import get_collection_models
from features.registry import FeatureConfigurationError
import re

# ============================================================================
# Hack for MP-537
# Keep this url manually updated for the moment. Remove when MP-540 is completed
marco_openlayers_url = '/static/visualize/deps/openlayers/OpenLayers-marco-min.js'

import django.contrib.gis.forms.widgets
django.contrib.gis.forms.widgets.OpenLayersWidget.Media.js = (
    marco_openlayers_url,
    'gis/js/OLMapWidget.js',
)

django.contrib.gis.forms.widgets.OSMWidget.Media.js = (
    marco_openlayers_url,
    'http://www.openstreetmap.org/openlayers/OpenStreetMap.js',
    'gis/js/OLMapWidget.js',
)
# End hack
# ============================================================================

urlpatterns = []
for model in registered_models:
    options = model.get_options()
    urlpatterns += [
        #'features.views',
        re_path(r'^%s/form/$' % (options.slug,), views.form_resources,
            kwargs={'model': model},
            name="%s_create_form" % (options.slug, )),

        re_path(r'^%s/(?P<uid>[\w_]+)/$' % (options.slug, ), views.resource,
            kwargs={'model': model},
            name='%s_resource' % (options.slug, )),

        re_path(r'^%s/(?P<uid>[\w_]+)/form/$' % (options.slug, ),
            views.form_resources, kwargs={'model': model},
            name='%s_update_form' % (options.slug,)),

        re_path(r'^%s/(?P<uid>[\w_]+)/share/$' % (options.slug, ),
            views.share_form, kwargs={'model': model},
            name='%s_share_form' % (options.slug,)),
    ]

for model in get_collection_models():
    options = model.get_options()
    urlpatterns += [
        #'features.views',
        re_path(r'^%s/(?P<collection_uid>[\w_]+)/remove/(?P<uids>[\w_,]+)$' % (options.slug, ),
            views.manage_collection, kwargs={'collection_model': model, 'action': 'remove'},
            name='%s_remove_features' % (options.slug,)),

        re_path(r'^%s/(?P<collection_uid>[\w_]+)/add/(?P<uids>[\w_,]+)$' % (options.slug, ),
            views.manage_collection, kwargs={'collection_model': model, 'action': 'add'},
            name='%s_add_features' % (options.slug,)),
    ]

for link in registered_links:
    path = r'^%s/links/%s/(?P<uids>[\w_,]+)/$' % (link.parent_slug, link.slug)
    urlpatterns += [
        #'features.views',
        re_path(path, views.handle_link, kwargs={'link': link},
            name=link.url_name)
    ]

urlpatterns += [
    #'features.views',
    re_path(r'^(?P<username>.+)/workspace-owner.json', views.workspace, kwargs={"is_owner": True}, name='workspace-owner-json'),
    re_path(r'^(?P<username>.+)/workspace-shared.json', views.workspace, kwargs={"is_owner": False}, name='workspace-shared-json'),
    re_path(r'^workspace-public.json', views.workspace, kwargs={"is_owner": False, "username": ''}, name='workspace-public-json'),
    re_path(r'^feature_tree.css', views.feature_tree_css, name='feature-tree-css'),
]
