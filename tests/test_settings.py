# Minimal settings file required to run tests.
import os

SECRET_KEY = 'poodles-puddles'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'tests',
    'features',
    # 'manipulators',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'some.db',
    }
}

ROOT_URLCONF = 'tests.urls'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# ----

# Madrona-features settings

SPATIALITE_LIBRARY_PATH = os.path.expanduser('~/root/brew/lib/mod_spatialite.dylib')
SHARING_TO_PUBLIC_GROUPS = ['Share with Public']
SHARING_TO_STAFF_GROUPS = ['Share with Staff']
TITLES = {
    'self': 'View',
}

GEOMETRY_CLIENT_SRID = 3857
GEOMETRY_DB_SRID = 3857
GEOJSON_DOWNLOAD = True
GEOJSON_SRID = 3857
