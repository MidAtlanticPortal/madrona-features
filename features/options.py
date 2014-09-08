from features.forms import FeatureForm

class FeatureOptions:
    """
    Represents properties of Feature Classes derived from both defaults and
    developer-specified options within the Options inner-class. These 
    properties drive the features of the spatial content managment system, 
    such as CRUD operations, copy, sharing, etc.

    """
    def __init__(self, model):

        # Import down here to avoid circular reference
        from features.models import Feature, FeatureCollection    

        # call this here to ensure that permsissions get created
        #enable_sharing()

        if not issubclass(model, Feature):
            raise FeatureConfigurationError('Is not a subclass of \
madrona.features.models.Feature')

        self._model = model
        name = model.__name__

        if not getattr(model, 'Options', False):
            raise FeatureConfigurationError(
                'Have not defined Options inner-class on registered feature \
class %s' % (name, ))

        self._options = model.Options

        if not hasattr(self._options, 'form'):
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a form class. \
To specify, add a `form` property to its Options inner-class." % (name,))

        if not isinstance(self._options.form, str):
            raise FeatureConfigurationError(
                "Feature class %s is configured with a form property that is \
not a string path." % (name,))

        self.form = self._options.form
        """
        Path to FeatureForm used to edit this class.
        """

        self.slug = slugify(name)
        """
        Name used in the url path to this feature as well as part of 
        the Feature's uid
        """

        self.verbose_name = getattr(self._options, 'verbose_name', name)
        """
        Name specified or derived from the feature class name used 
        in the user interface for representing this feature class.
        """

        self.form_template = getattr(self._options, 'form_template', 
            'features/form.html')
        """
        Location of the template that should be used to render forms
        when editing or creating new instances of this feature class.
        """

        self.form_context = getattr(self._options, 'form_context', {})
        """
        Context to merge with default context items when rendering
        templates to create or modify features of this class.
        """

        self.show_context = getattr(self._options, 'show_context', {})
        """
        Context to merge with default context items when rendering
        templates to view information about instances of this feature class.
        """

        self.icon_url = getattr(self._options, 'icon_url', None)
        """
        Optional; URL to 16x16 icon to use in kmltree
        Use full URL or relative to MEDIA_URL
        """

        self.links = []
        """
        Links associated with this class.
        """

        opts_links = getattr(self._options, 'links', False)
        if opts_links:
            self.links.extend(opts_links)

        self.enable_copy = getattr(self._options, 'disable_copy', True)
        """
        Enable copying features. Uses the feature class' copy() method. 
        Defaults to True.
        """

        # Add a copy method unless disabled
        if self.enable_copy:
            self.links.insert(0, edit('Copy', 
                'madrona.features.views.copy', 
                select='multiple single',
                edits_original=False))

        confirm = "Are you sure you want to delete this feature and it's contents?"

        # Add a multi-share generic link
        # TODO when the share_form view takes multiple instances
        #  we can make sharing a generic link 
        #self.links.insert(0, edit('Share', 
        #    'madrona.features.views.share_form', 
        #    select='multiple single',
        #    method='POST',
        #    edits_original=True,
        #))

        # Add a multi-delete generic link
        self.links.insert(0, edit('Delete', 
            'madrona.features.views.multi_delete', 
            select='multiple single',
            method='DELETE',
            edits_original=True,
            confirm=confirm,
        ))

        # Add a staticmap generic link
        export_png = getattr(self._options, 'export_png', True)
        if export_png:
            self.links.insert(0, alternate('PNG Image', 
                'madrona.staticmap.views.staticmap_link', 
                select='multiple single',
                method='GET',
            ))

        # Add a geojson generic link
        export_geojson = getattr(self._options, 'export_geojson', True)
        if export_geojson:
            self.links.insert(0, alternate('GeoJSON', 
                'madrona.features.views.geojson_link', 
                select='multiple single',
                method='GET',
            ))

        self.valid_children = getattr(self._options, 'valid_children', None)
        """
        valid child classes for the feature container
        """
        if self.valid_children and not issubclass(self._model, FeatureCollection):
            raise FeatureConfigurationError("valid_children Option only \
                    for FeatureCollection classes" % m)

        self.manipulators = [] 
        """
        Required manipulators applied to user input geometries
        """
        manipulators = getattr(self._options, 'manipulators', []) 
        for m in manipulators:
            try:
                manip = get_class(m)
            except:
                raise FeatureConfigurationError("Error trying to import module %s" % m)

            # Test that manipulator is compatible with this Feature Class
            geom_field = self._model.geometry_final._field.__class__.__name__ 
            if geom_field not in manip.Options.supported_geom_fields:
                raise FeatureConfigurationError("%s does not support %s geometry types (only %r)" %
                        (m, geom_field, manip.Options.supported_geom_fields))

            #logger.debug("Added required manipulator %s" % m)
            self.manipulators.append(manip)

        self.optional_manipulators = []
        """
        Optional manipulators that may be applied to user input geometries
        """
        optional_manipulators = getattr(self._options, 'optional_manipulators', [])
        for m in optional_manipulators:
            try:
                manip = get_class(m)
            except:
                raise FeatureConfigurationError("Error trying to import module %s" % m)

            # Test that manipulator is compatible with this Feature Class
            geom_field = self._model.geometry_final._field.__class__.__name__ 
            try:
                if geom_field not in manip.Options.supported_geom_fields:
                    raise FeatureConfigurationError("%s does not support %s geometry types (only %r)" %
                        (m, geom_field, manip.Options.supported_geom_fields))
            except AttributeError:
                raise FeatureConfigurationError("%s is not set up properly; must have "
                        "Options.supported_geom_fields list." % m)

            #logger.debug("Added optional manipulator %s" % m)
            self.optional_manipulators.append(manip)

        self.enable_kml = True
        """
        Enable kml visualization of features.  Defaults to True.
        """
        # Add a kml link by default
        if self.enable_kml:
            self.links.insert(0,alternate('KML',
                'madrona.features.views.kml',
                select='multiple single'))
            self.links.insert(0,alternate('KMZ',
                'madrona.features.views.kmz',
                select='multiple single'))

        for link in self.links:
            if self._model not in link.models:
                link.models.append(self._model)

    def get_show_template(self):
        """
        Returns the template used to render this Feature Class' attributes
        """
        # Grab a template specified in the Options object, or use the default
        template = getattr(self._options, 'show_template', 
            '%s/show.html' % (self.slug, ))
        try:
            t = loader.get_template(template)
        except TemplateDoesNotExist:
            # If a template has not been created, use a stub that displays
            # some documentation on how to override the default template
            t = loader.get_template('features/show.html')
        return t

    def get_link(self,linkname):
        """
        Returns the FeatureLink with the specified name
        """
        try:
            link = [x for x in self.links if x.title == linkname][0]
            return link
        except:
            raise Exception("%r has no link named %s" % (self._model, linkname))

    def get_valid_children(self):
        if not self.valid_children:
            raise FeatureConfigurationError(
                "%r is not a properly configured FeatureCollection" % (self._model))

        valid_child_classes = []
        for vc in self.valid_children:
            try:
                vc_class = get_class(vc)
            except:
                raise FeatureConfigurationError(
                        "Error trying to import module %s" % vc) 

            from madrona.features.models import Feature
            if not issubclass(vc_class, Feature):
                raise FeatureConfigurationError(
                        "%r is not a Feature; can't be a child" % vc) 

            valid_child_classes.append(vc_class)

        return valid_child_classes

    def get_potential_parents(self):
        """
        It's not sufficient to look if this model is a valid_child of another
        FeatureCollection; that collection could contain other collections 
        that contain this model. 

        Ex: Folder (only valid child is Array)
            Array (only valid child is MPA)
            Therefore, Folder is also a potential_parent of MPA
        """
        potential_parents = []
        direct_parents = []
        collection_models = get_collection_models()
        for model in collection_models: 
            opts = model.get_options()
            valid_children = opts.get_valid_children()

            if self._model in valid_children:
                direct_parents.append(model)
                potential_parents.append(model)

        for direct_parent in direct_parents:
            if direct_parent != self._model: 
                potential_parents.extend(direct_parent.get_options().get_potential_parents())

        return potential_parents 

    def get_form_class(self):
        """
        Returns the form class for this Feature Class.
        """
        try:
            klass = get_class(self.form)
        except Exception, e:
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a valid form class. \
Could not import %s.\n%s" % (self._model.__name__, self.form, e))

        if not issubclass(klass, FeatureForm):
            raise FeatureConfigurationError(
                "Feature class %s's form is not a subclass of \
madrona.features.forms.FeatureForm." % (self._model.__name__, ))

        return klass

    def dict(self,user,is_owner):
        """
        Returns a json representation of this feature class configuration
        that can be used to specify client behavior
        """
        placeholder = "%s_%d" % (self._model.model_uid(), 14)
        link_rels = {
            'id': self._model.model_uid(),
            'title': self.verbose_name,
            'link-relations': {
                'self': {
                    'uri-template': reverse("%s_resource" % (self.slug, ), 
                        args=[placeholder]).replace(placeholder, '{uid}'),
                    'title': settings.TITLES['self'],
                },
            }
        }

        if is_owner:
            lr = link_rels['link-relations']
            lr['create'] = {
                    'uri-template': reverse("%s_create_form" % (self.slug, ))
            }

            lr['edit'] = [
                    {'title': 'Edit',
                      'uri-template': reverse("%s_update_form" % (self.slug, ), 
                        args=[placeholder]).replace(placeholder, '{uid}')
                    },
                    {'title': 'Share',
                      'uri-template': reverse("%s_share_form" % (self.slug, ), 
                        args=[placeholder]).replace(placeholder, '{uid}')
                    }]

        for link in self.links:
            if not link.generic and link.can_user_view(user, is_owner):
                if link.rel not in link_rels['link-relations'].keys():
                    if not (user.is_anonymous() and link.rel == 'edit'):
                        link_rels['link-relations'][link.rel] = []
                link_rels['link-relations'][link.rel].append(link.dict(user,is_owner))

        if self._model in get_collection_models() and is_owner:
            link_rels['collection'] = {
                'classes': [x.model_uid() for x in self.get_valid_children()],
                'remove': {
                    'uri-template': reverse("%s_remove_features" % (self.slug, ), 
                        kwargs={'collection_uid':14,'uids':'xx'}).replace('14', '{collection_uid}').replace('xx','{uid+}')
                },
                'add': {
                    'uri-template': reverse("%s_add_features" % (self.slug, ), 
                        kwargs={'collection_uid':14,'uids':'xx'}).replace('14', '{collection_uid}').replace('xx','{uid+}')
                }

            }
        return link_rels

    def json(self):
        return json.dumps(self.dict())

    def get_create_form(self):
        """
        Returns the path to a form for creating new instances of this model
        """
        return reverse('%s_create_form' % (self.slug, ))

    def get_update_form(self, pk):
        """
        Given a primary key, returns the path to a form for updating a Feature
        Class
        """
        return reverse('%s_update_form' % (self.slug, ), args=['%s_%d' % (self._model.model_uid(), pk)])

    def get_share_form(self, pk):
        """
        Given a primary key, returns path to a form for sharing a Feature inst
        """
        return reverse('%s_share_form' % (self.slug, ), args=['%s_%d' % (self._model.model_uid(), pk)])

    def get_resource(self, pk):
        """
        Returns the primary url for a feature. This url supports GET, POST, 
        and DELETE operations.
        """
        return reverse('%s_resource' % (self.slug, ), args=['%s_%d' % (self._model.model_uid(), pk)])
