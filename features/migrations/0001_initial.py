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

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(MARCO_ALBERS_SQL, REVERSE_MARCO_ALBERS_SQL),
    ]
