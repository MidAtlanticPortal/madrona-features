from django.db import models
from features.registry import register, alternate, related, edit, edit_form
from features.models import Feature, PolygonFeature, FeatureCollection, \
    LineFeature, PointFeature, MultiPolygonFeature

# Lets use the following as a canonical example of how to use all the features
# of this framework (will be kept up to date as api changes):
from nursery.jsonutils import get_properties_json
from nursery.jsonutils import get_feature_json

DESIGNATION_CHOICES = (
    ('R', 'Reserve'),
    ('P', 'Park'),
    ('C', 'Conservation Area')
)


@register
class TestMpa(PolygonFeature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)

    class Options:
        verbose_name = 'Marine Protected Area'
        form = 'tests.forms.MpaForm'
        manipulators = ['manipulators.tests.TestManipulator']
        optional_manipulators = [
            'manipulators.manipulators.ClipToGraticuleManipulator']
        links = (
            related('Habitat Spreadsheet',
                    'tests.views.habitat_spreadsheet',
                    select='single',
                    type='application/xls',
                    limit_to_groups=['SuperSpecialTestGroup']
            ),
            alternate('Export KML for Owner',
                      'tests.views.kml',
                      select='multiple single',
                      must_own=True
            ),
            alternate('Export KML',
                      'tests.views.kml',
                      select='multiple single'
            ),
            alternate('Export Misc for Owner',
                      'tests.views.kml',
                      select='multiple single',
                      must_own=True
            )
        )


@register
class TestForGeoJSON(PolygonFeature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)

    class Options:
        form = 'tests.forms.GJForm'

    def geojson(self, srid):
        import json

        props = get_properties_json(self)
        props['absolute_url'] = self.get_absolute_url()
        jsongeom = self.geometry_final.transform(srid, clone=True).json
        return get_feature_json(jsongeom, json.dumps(props))


@register
class TestNoGeomFinal(Feature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)
    # just a base feature so no geometry_final attribute
    class Options:
        form = 'tests.forms.GJFormNoGeom'


@register
class TestNoGeoJSON(PolygonFeature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)

    class Options:
        form = 'tests.forms.TestNoGeoJSONForm'
        export_geojson = False


@register
class TestGetFormClassFeature(Feature):
    class Options:
        form = 'tests.forms.TestFeatureForm'


@register
class TestGetFormClassFailFeature(Feature):
    class Options:
        form = 'tests.forms.TestForm'


@register
class TestSlugFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'


@register
class TestDefaultVerboseNameFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'


@register
class TestCustomVerboseNameFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'
        verbose_name = 'vb-name'


@register
class TestDefaultShowTemplateFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'


@register
class TestCustomShowTemplateFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'
        show_template = 'location/show.html'


@register
class TestMissingDefaultShowFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'


@register
class TestMissingCustomShowFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'
        show_template = 'location/show.html'


@register
class TestDeleteFeature(Feature):
    class Options:
        form = 'tests.forms.FeatureForm'


@register
class CreateFormTestFeature(Feature):
    class Options:
        form = 'tests.forms.CreateFormTestForm'


@register
class CreateTestFeature(Feature):
    class Options:
        form = 'tests.forms.CreateTestForm'


@register
class UpdateFormTestFeature(Feature):
    class Options:
        form = 'tests.forms.UpdateFormTestForm'


@register
class UpdateTestFeature(Feature):
    class Options:
        form = 'tests.forms.UpdateTestForm'


@register
class LinkTestFeature(Feature):
    class Options:
        form = 'tests.forms.LinkTestFeatureForm'
        links = (
            alternate('Single Select View',
                      'tests.views.valid_single_select_view',
                      type="application/shapefile"),

            alternate('Spreadsheet of all Features',
                      'tests.views.valid_multiple_select_view',
                      type="application/xls",
                      select='multiple single'),

            edit('Edit single feature',
                 'tests.views.valid_single_select_view'
            ),

            edit_form('Edit multiple features',
                      'tests.views.valid_multiple_select_view',
                      select='multiple single'
            ),
        )


@register
class GenericLinksTestFeature(Feature):
    class Options:
        form = 'tests.forms.GenericLinksTestForm'
        links = (
            alternate('Generic Link',
                      'tests.views.multi_select_view',
                      type="application/shapefile",
                      select='multiple single'),
            alternate('Non-Generic Link',
                      'tests.views.multi_select_view',
                      type="application/shapefile",
                      select='multiple single'),
        )


@register
class OtherGenericLinksTestFeature(Feature):
    class Options:
        form = 'tests.forms.OtherGenericLinksTestForm'
        links = (
            alternate('Generic Link',
                      'tests.views.multi_select_view',
                      type="application/shapefile",
                      select='multiple single'),
        )


@register
class LastGenericLinksTestFeature(Feature):
    class Options:
        form = 'tests.forms.GenericLinksTestForm'
        links = (
            alternate('Different Name',
                      'tests.views.multi_select_view',
                      type="application/shapefile",
                      select='multiple single'),

        )


@register
class TestArray(FeatureCollection):
    class Options:
        form = 'tests.forms.TestArrayForm'
        valid_children = (
            'tests.models.TestMpa',
            'tests.models.Pipeline',
            'tests.models.RenewableEnergySite')


@register
class TestFolder(FeatureCollection):
    def copy(self, user):
        copy = super(TestFolder, self).copy(user)
        copy.name = copy.name.replace(' (copy)', '-Copy')
        copy.save()
        return copy

    class Options:
        form = 'tests.tests.TestFolderForm'
        valid_children = (
            'tests.models.TestMpa',
            'tests.models.TestArray',
            'tests.models.TestFolder',
            'tests.models.TestDeleteFeature',
            'tests.models.RenewableEnergySite')
        links = (
            edit('Delete folder and contents',
                 'tests.views.delete_w_contents',
                 select='single multiple',
                 confirm="""
                Are you sure you want to delete this folder and it's contents?
                This action cannot be undone.
                """
            ),
            alternate('Export KML for Owner',
                      'tests.views.kml',
                      select='multiple single',
                      must_own=True
            ),
            alternate('Export KML',
                      'tests.views.kml',
                      select='multiple single'
            )
        )


TYPE_CHOICES = (
    ('W', 'Wind'),
    ('H', 'Hydrokinetic'),
)


@register
class RenewableEnergySite(PolygonFeature):
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    class Options:
        verbose_name = 'Renewable Energy Site'
        form = 'tests.views.RenewableEnergySiteForm'
        links = (
            related('Viewshed Map',
                    'tests.views.viewshed_map',
                    select='single',
                    type='image/png'
            ),
            alternate('Export KML',
                      'tests.views.kml',
                      select='multiple single'
            )
        )


@register
class Pipeline(LineFeature):
    type = models.CharField(max_length=30, default='')
    diameter = models.FloatField(null=True)

    class Options:
        verbose_name = 'Pipeline'
        form = 'tests.forms.PipelineForm'


@register
class Shipwreck(PointFeature):
    incident = models.CharField(max_length=100, default='')

    class Options:
        verbose_name = 'Shipwreck'
        form = 'tests.forms.ShipwreckForm'


@register
class MockMultiPoly(MultiPolygonFeature):
    class Options:
        verbose_name = 'Marine Protected Area multipolygon'
        form = 'tests.forms.TestMultiPolyForm'
        manipulators = []
