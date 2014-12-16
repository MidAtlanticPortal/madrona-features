# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

MARCO_ALBERS_SQL = '''
insert into spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) 
values (99996, 'EPSG', 99996, 'Marco Albers', '+proj=aea +lat_1=37.25 +lat_2=40.25 +lat_0=36 +lon_0=-72 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs');
'''

REVERSE_MARCO_ALBERS_SQL = '''
delete from spatial_ref_sys where srid = 99996 limit 1;
'''

GIS_GEOMETRY_OPS_SQL = '''
CREATE OPERATOR CLASS gist_geometry_ops
FOR TYPE geometry USING GIST AS
STORAGE box2df,
OPERATOR        1        <<  ,
OPERATOR        2        &<  ,
OPERATOR        3        &&  ,
OPERATOR        4        &>  ,
OPERATOR        5        >>  ,
OPERATOR        6        ~=  ,
OPERATOR        7        ~   ,
OPERATOR        8        @   ,
OPERATOR        9        &<| ,
OPERATOR        10       <<| ,
OPERATOR        11       |>> ,
OPERATOR        12       |&> ,

OPERATOR        13       <-> FOR ORDER BY pg_catalog.float_ops,
OPERATOR        14       <#> FOR ORDER BY pg_catalog.float_ops,
FUNCTION        8        geometry_gist_distance_2d (internal, geometry, int4),

FUNCTION        1        geometry_gist_consistent_2d (internal, geometry, int4),
FUNCTION        2        geometry_gist_union_2d (bytea, internal),
FUNCTION        3        geometry_gist_compress_2d (internal),
FUNCTION        4        geometry_gist_decompress_2d (internal),
FUNCTION        5        geometry_gist_penalty_2d (internal, internal, internal),
FUNCTION        6        geometry_gist_picksplit_2d (internal, internal),
FUNCTION        7        geometry_gist_same_2d (geom1 geometry, geom2 geometry, internal);
'''

REVERSE_GIS_GEOMETRY_OPS_SQL = '''
drop operator class if exists gist_geometry_ops using gist;
'''

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(MARCO_ALBERS_SQL, REVERSE_MARCO_ALBERS_SQL),
        migrations.RunSQL(GIS_GEOMETRY_OPS_SQL, REVERSE_GIS_GEOMETRY_OPS_SQL),
    ]
