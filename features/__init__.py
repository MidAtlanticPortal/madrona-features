# TODO: Remove code from __init__ and put it somewhere appropriate

import logging
from django.template.defaultfilters import slugify
from django.template import loader, TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, class_prepared
from django.dispatch import receiver
from django.contrib.auth.models import Permission, Group
from django.conf import settings
from django.db.utils import DatabaseError
import json

registered_models = []
registered_model_options = {}
registered_links = []
logger = logging.getLogger('madrona.features')


# Two functions brought from madrona.common.utils so we don't have a dependency
# on that module anymore. 
# TODO: Find a home for them.
# TODO: Refactor so they don't import modules

def get_class(path):
    from django.utils import importlib
    module, dot, cls = path.rpartition('.')
    m = importlib.import_module(module)
    return m.__getattribute__(cls)
 
def enable_sharing(group=None):
    """
    Give group permission to share models 
    Permissions are attached to models but we want this perm to be 'global'
    Fake it by attaching the perm to the Group model (from the auth app)
    We check for this perm like: user1.has_perm("auth.can_share_features")
    """
    from django.contrib.auth.models import Permission, Group
    from django.contrib.contenttypes.models import ContentType

    try:
        p = Permission.objects.get(codename='can_share_features')
    except Permission.DoesNotExist:
        gct = ContentType.objects.get(name="group")
        p = Permission.objects.create(codename='can_share_features',name='Can Share Features',content_type=gct)
        p.save()

    # Set up default sharing groups
    for groupname in settings.SHARING_TO_PUBLIC_GROUPS:
        g, created = Group.objects.get_or_create(name=groupname)
        g.permissions.add(p)
        g.save()

    for groupname in settings.SHARING_TO_STAFF_GROUPS:
        g, created = Group.objects.get_or_create(name=groupname)
        g.permissions.add(p)
        g.save()

    if group:
        # Set up specified group
        group.permissions.add(p)
        group.save()
    return True





class FeatureConfigurationError(Exception):
    pass

class Link:
    def __init__(self, rel, title, view, method='GET', select='single', 
        type=None, slug=None, generic=False, models=None, extra_kwargs={}, 
        confirm=False, edits_original=None, must_own=False, 
        limit_to_groups=None):

        self.rel = rel
        """Type of link - alternate, related, edit, or edit_form.
        """

        try:
            self.view = get_class(view)
            """
            View function handling requests to this link.
            """
        except Exception as err:
            msg = 'Link "%s" configured with invalid path to view %s' % (title, view)
            msg += '\n%s\n' % str(err)
            if "cannot import" in str(err):
                msg += "(Possible cause: importing Features at the top level in views.py can cause"
                msg += " circular dependencies; Try to import Features within the view function)"

            raise FeatureConfigurationError(msg)

        self.title = title
        """
        Human-readable title for the link to be shown in the user interface.
        """

        self.method = method
        """
        For rel=edit links, identifies whether a form should be requested or 
        that url should just be POST'ed to.
        """

        self.type = type
        """
        MIME type of this link, useful for alternate links. May in the future
        be used to automatically assign an icon in the dropdown Export menu.
        """

        self.slug = slug
        """
        Part of this link's path.
        """

        self.select = select
        """
        Determines whether this link accepts requests with single or multiple
        instances of a feature class. Valid values are "single", "multiple",
        "single multiple", and "multiple single". 
        """

        self.extra_kwargs = extra_kwargs
        """
        Extra keyword arguments to pass to the view.
        """

        self.generic = generic
        """
        Whether this view can be applied to multiple feature classes.
        """

        self.models = models
        """
        List of feature classes that a this view can be applied to, if it is 
        generic.
        """

        self.confirm = confirm
        """
        Confirmation message to show the user before POSTing to rel=edit link
        """

        self.edits_original = edits_original
        """
        Set to false for editing links that create a copy of the original. 
        This will allow users who do not own the instance(s) but can view them
        perform the action.
        """

        self.must_own = must_own
        if self.edits_original:
            self.must_own = True
        """
        Whether this link should be accessible to non-owners.
        Default link behavior is False; i.e. Link can be used for shared features
        as well as for user-owned features. 
        If edits_original is true, this implies must_own = True as well.
        """

        self.limit_to_groups = limit_to_groups
        """
        Allows you to specify groups (a list of group names) 
        that should have access to the link.
        Default is None; i.e. All users have link access regardless of group membership
        """

        if self.models is None:
            self.models = []

        # Make sure title isn't empty
        if self.title is '':
            raise FeatureConfigurationError('Link title is empty')
        valid_options = ('single', 'multiple', 'single multiple', 
            'multiple single')
        # Check for valid 'select' kwarg
        if self.select not in valid_options:
            raise FeatureConfigurationError(
                'Link specified with invalid select option "%s"' % (
                    self.select, ))
        # Create slug from the title unless a custom slug is specified
        if self.slug is None:
            self.slug = slugify(title)
        # Make sure the view has the right signature
        self._validate_view(self.view)

    def _validate_view(self, view):
        """
        Ensures view has a compatible signature to be able to hook into the 
        features app url registration facilities

        For single-select views
            must accept a second argument named instance
        For multiple-select views
            must accept a second argument named instances

        Must also ensure that if the extra_kwargs option is specified, the 
        view can handle them
        """
        # Check for instance or instances arguments
        if self.select is 'single':
            args = view.__code__.co_varnames
            if len(args) < 2 or args[1] != 'instance':
                raise FeatureConfigurationError('Link "%s" not configured \
with a valid view. View must take a second argument named instance.' % (
self.title, ))
        else:
            # select="multiple" or "multiple single" or "single multiple"
            args = view.__code__.co_varnames
            if len(args) < 2 or args[1] != 'instances':
                raise FeatureConfigurationError('Link "%s" not configured \
with a valid view. View must take a second argument named instances.' % (
self.title, ))

    def can_user_view(self, user, is_owner):
        """
        Returns True/False depending on whether user can view the link. 
        """
        if self.limit_to_groups:
            # We rely on the auth Group model ensuring unique group names
            user_groupnames = [x.name for x in user.groups.all()]
            match = False
            for groupname in self.limit_to_groups:
                if groupname in user_groupnames:
                    match = True
                    break
            if not match:
                return False

        if self.must_own and not is_owner:
            return False

        return True

    @property
    def url_name(self):
        """
        Links are registered with named-urls. This function will return 
        that name so that it can be used in calls to reverse().
        """
        return "%s-%s" % (self.parent_slug, self.slug)

    @property
    def parent_slug(self):
        """
        Returns either the slug of the only model this view applies to, or 
        'generic'
        """
        if len(self.models) == 1:
            return self.models[0].get_options().slug
        else:
            return 'generic-links'

    def reverse(self, instances):
        """Can be used to get the url for this link. 

        In the case of select=single links, just pass in a single instance. In
        the case of select=multiple links, pass in an array.
        """
        if not isinstance(instances,tuple) and not isinstance(instances,list):
            instances = [instances]
        uids = ','.join([instance.uid for instance in instances])
        return reverse(self.url_name, kwargs={'uids': uids})

    def __str__(self):
        return self.title

    def __unicode__(self):
        return str(self)

    def dict(self,user,is_owner):
        d = {
            'rel': self.rel,
            'title': self.title,
            'select': self.select,
            'uri-template': reverse(self.url_name, 
                kwargs={'uids': 'idplaceholder'}).replace(
                    'idplaceholder', '{uid+}')
        }
        if self.rel == 'edit':
            d['method'] = self.method
        if len(self.models) > 1:
            d['models'] = [m.model_uid() for m in self.models]
        if self.confirm:
            d['confirm'] = self.confirm
        return d

    def json(self):
        return json.dumps(self.dict())

def create_link(rel, *args, **kwargs):
    nargs = [rel]
    nargs.extend(args)
    link = Link(*nargs, **kwargs)
    must_match = ('rel', 'title', 'view', 'extra_kwargs', 'method', 'slug', 
        'select', 'must_own')
    for registered_link in registered_links:
        matches = True
        for key in must_match:
            if getattr(link, key) != getattr(registered_link, key):
                matches = False
                break
        if matches:
            registered_link.generic = True
            return registered_link
    registered_links.append(link)
    return link

def alternate(*args, **kwargs):
    return create_link('alternate', *args, **kwargs)

def related(*args, **kwargs):
    return create_link('related', *args, **kwargs)

def edit(*args, **kwargs):
    if 'method' not in kwargs.keys():
        kwargs['method'] = 'POST'
    return create_link('edit', *args, **kwargs)

def edit_form(*args, **kwargs):
    if 'method' not in kwargs.keys():
        kwargs['method'] = 'GET'
    return create_link('edit', *args, **kwargs)

def register(model):
    from .options import FeatureOptions
    options = FeatureOptions(model)
    logger.debug('registering Feature %s' % (model.__name__,))
    if model not in registered_models:
        registered_models.append(model)
        registered_model_options[model.__name__] = options
        for link in options.links:
            if link not in registered_links:
                registered_links.append(link)
    return model

def get_model_options(model_name):
    return registered_model_options[model_name]

def workspace_json(user, is_owner, models=None):
    workspace = {
        'feature-classes': [],
        'generic-links': []
    }
    if not models:
        # Workspace doc gets ALL feature classes and registered links
        for model in registered_models:
            workspace['feature-classes'].append(model.get_options().dict(user, is_owner))
        for link in registered_links:
            if link.generic and link.can_user_view(user, is_owner) \
                    and not (user.is_anonymous() and link.rel == 'edit'):
                workspace['generic-links'].append(link.dict(user, is_owner))
    else:
        # Workspace doc only reflects specified feature class models
        for model in models:
            workspace['feature-classes'].append(model.get_options().dict(user, is_owner))
        for link in registered_links:
            # See if the generic links are relavent to this list
            if link.generic and \
               [i for i in args if i in link.models] and \
               link.can_user_view(user, is_owner) and \
               not (user.is_anonymous() and link.rel == 'edit'):
                    workspace['generic-links'].append(link.dict(user, is_owner))
    return json.dumps(workspace, indent=2)

def get_collection_models():
    """
    Utility function returning models for 
    registered and valid FeatureCollections
    """
    from madrona.features.models import FeatureCollection    
    registered_collections = []
    for model in registered_models:
        if issubclass(model,FeatureCollection):
            opts = model.get_options()
            try:
                assert len(opts.get_valid_children()) > 0
                registered_collections.append(model)
            except:
                pass
    return registered_collections

def get_feature_models():
    """
    Utility function returning models for 
    registered and valid Features excluding Collections
    """
    from madrona.features.models import Feature, FeatureCollection
    registered_features = []
    for model in registered_models:
        if issubclass(model,Feature) and not issubclass(model,FeatureCollection):
            registered_features.append(model)
    return registered_features

def user_sharing_groups(user):
    """
    Returns a list of groups that user is member of and 
    and group must have sharing permissions
    """
    try:
        p = Permission.objects.get(codename='can_share_features')
    except Permission.DoesNotExist:
        return None

    groups = user.groups.filter(permissions=p).distinct()
    return groups

def groups_users_sharing_with(user, include_public=False):
    """
    Get a dict of groups and users that are currently sharing items with a given user
    If spatial_only is True, only models which inherit from the Feature class will be reflected here
    returns something like {'our_group': {'group': <Group our_group>, 'users': [<user1>, <user2>,...]}, ... }
    """
    groups_sharing = {}

    for model_class in registered_models:
        shared_objects = model_class.objects.shared_with_user(user)
        for group in user.groups.all():
            # Unless overridden, public shares don't show up here
            if group.name in settings.SHARING_TO_PUBLIC_GROUPS and not include_public:
                continue
            # User has to be staff to see these
            if group.name in settings.SHARING_TO_STAFF_GROUPS and not user.is_staff:
                continue
            group_objects = shared_objects.filter(sharing_groups=group)
            user_list = []
            for gobj in group_objects:
                if gobj.user not in user_list and gobj.user != user:
                    user_list.append(gobj.user)

            if len(user_list) > 0:
                if group.name in groups_sharing.keys():
                    for user in user_list:
                        if user not in groups_sharing[group.name]['users']:
                            groups_sharing[group.name]['users'].append(user)
                else:
                    groups_sharing[group.name] = {'group':group, 'users': user_list}
    if len(groups_sharing.keys()) > 0:
        return groups_sharing
    else:
        return None

def get_model_by_uid(muid):
    for model in registered_models:
        if model.model_uid() == muid:
            return model
    raise Exception("No model with model_uid == `%s`" % muid)

def get_feature_by_uid(uid):
    applabel, modelname, id = uid.split('_')
    id = int(id)
    model = get_model_by_uid("%s_%s" % (applabel,modelname))
    instance = model.objects.get(pk=int(id))
    return instance
