from django.urls import path
from rest_framework_nested import routers

from . import views

urlpatterns = [
    path('phasors/<int:id>/', views.PhasorView.as_view()),
    path('harmonics/<int:id>/<int:start>/<int:end>/', views.HarmonicsView.as_view()),
]

router = routers.DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='projects')
projects_router = routers.NestedDefaultRouter(router, 'projects', lookup='project')
projects_router.register('files', views.FileViewSet, basename='project-files')

# files_router = routers.NestedDefaultRouter(router, 'files', lookup='files')
# files_router.register('achannels', views.AnalogChannelViewSet, basename='project-files-achannels')

router.register('files', views.AllFilesViewSet, basename='files')
files_router = routers.NestedDefaultRouter(router, 'files', lookup='file')
files_router.register('achannels', views.AnalogChannelViewSet, basename='files-achannels')
files_router.register('dchannels', views.DigitalChannelViewSet, basename='files-dchannels')
files_router.register('asignals', views.AnalogSignalViewSet, basename='files-asignals')
files_router.register('dsignals', views.DigtialSignalViewSet, basename='files-dsignals')

urlpatterns += router.urls + projects_router.urls + files_router.urls

# END-POINTS
# -----------
# http://127.0.0.1:8000/comtrade_reader/projects/
# http://127.0.0.1:8000/comtrade_reader/projects/1/
# http://127.0.0.1:8000/comtrade_reader/projects/1/files/
# http://127.0.0.1:8000/comtrade_reader/projects/1/files/1/

# http://127.0.0.1:8000/comtrade_reader/files/  => no viewing
# http://127.0.0.1:8000/comtrade_reader/files/1/achannels/
# http://127.0.0.1:8000/comtrade_reader/files/1/dchannels/
# http://127.0.0.1:8000/comtrade_reader/files/1/achannels/1/
# http://127.0.0.1:8000/comtrade_reader/files/1/dchannels/1/

# http://127.0.0.1:8000/comtrade_reader/files/1/asignals/
# http://127.0.0.1:8000/comtrade_reader/files/1/dsignals/

# http://127.0.0.1:8000/comtrade_reader/phasors/<file_id>/
# http://127.0.0.1:8000/comtrade_reader/harmonics/<file_id>/<start_sample>/<end_sample>/