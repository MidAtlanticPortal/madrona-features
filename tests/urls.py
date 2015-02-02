from django.conf.urls import url, include
import features.urls

urlpatterns = [
    url(r'^f/', include(features.urls.urls())),
]
