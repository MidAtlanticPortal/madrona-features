from .models import TestNoGeoJSON, TestMpa, TestForGeoJSON, \
    TestNoGeomFinal, TestGetFormClassFeature, CreateFormTestFeature, \
    CreateTestFeature, UpdateFormTestFeature, Pipeline, LinkTestFeature, \
    RenewableEnergySite, UpdateTestFeature, GenericLinksTestFeature, \
    OtherGenericLinksTestFeature, Shipwreck, MockMultiPoly, TestFolder, \
    TestArray

from features.forms import FeatureForm


class MpaForm(FeatureForm):
    class Meta:
        model = TestMpa


class GJForm(FeatureForm):
    class Meta:
        model = TestForGeoJSON


class GJFormNoGeom(FeatureForm):
    class Meta:
        model = TestNoGeomFinal


class TestNoGeoJSONForm(FeatureForm):
    class Meta:
        model = TestNoGeoJSON


class TestFeatureForm(FeatureForm):
    class Meta:
        model = TestGetFormClassFeature


class TestForm:
    class Meta:
        model = TestGetFormClassFeature


class CreateFormTestForm(FeatureForm):
    class Meta:
        model = CreateFormTestFeature


class CreateTestForm(FeatureForm):
    class Meta:
        model = CreateTestFeature


class UpdateFormTestForm(FeatureForm):
    class Meta:
        model = UpdateFormTestFeature


class UpdateTestForm(FeatureForm):
    class Meta:
        model = UpdateTestFeature


class LinkTestFeatureForm(FeatureForm):
    class Meta:
        model = LinkTestFeature


class GenericLinksTestForm(FeatureForm):
    class Meta:
        model = GenericLinksTestFeature


class OtherGenericLinksTestForm(FeatureForm):
    class Meta:
        model = OtherGenericLinksTestFeature


class TestArrayForm(FeatureForm):
    class Meta:
        model = TestArray


class TestFolderForm(FeatureForm):
    class Meta:
        model = TestFolder


class RenewableEnergySiteForm(FeatureForm):
    class Meta:
        model = RenewableEnergySite


class PipelineForm(FeatureForm):
    class Meta:
        model = Pipeline


class ShipwreckForm(FeatureForm):
    class Meta:
        model = Shipwreck


class MockMultiPolyForm(FeatureForm):
    class Meta:
        model = MockMultiPoly
