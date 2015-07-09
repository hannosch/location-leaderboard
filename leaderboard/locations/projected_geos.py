from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Polygon, Point


class ProjectedMixin(object):

    def __init__(self, *args, **kwargs):
        return super(ProjectedMixin, self).__init__(
            *args, srid=settings.PROJECTION_SRID, **kwargs)


class ProjectedPoint(ProjectedMixin, Point):
    pass


class ProjectedPolygon(ProjectedMixin, Polygon):
    pass


class ProjectedMultiPolygon(ProjectedMixin, MultiPolygon):
    pass