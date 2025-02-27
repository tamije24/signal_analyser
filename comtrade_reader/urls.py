from django.urls import path
from rest_framework_nested import routers

from . import views

urlpatterns = [
    path('afa-projects-new/',views.ProjectAndFilesViewSet.as_view()),
    path('afa-projects/<afa_id>/', views.ProjectAFAView.as_view()),
    path('phasors/<int:id>/<int:src>/', views.PhasorView.as_view()),
    path('harmonics/<int:id>/<int:start>/<int:end>/<int:src>/', views.HarmonicsView.as_view()),
    path('asignals/<int:id>/<int:src>/', views.AnalogSignalView.as_view()),
    path('dsignals/<int:id>/<int:src>/', views.DigitalSignalView.as_view()),
    path('resample/<int:id>/<int:fsnew>/', views.ResampleView.as_view()),
]

router = routers.DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='projects')
projects_router = routers.NestedDefaultRouter(router, 'projects', lookup='project')
projects_router.register('files', views.FileViewSet, basename='project-files')

router.register('files', views.AllFilesViewSet, basename='files')
files_router = routers.NestedDefaultRouter(router, 'files', lookup='file')
files_router.register('achannels', views.AnalogChannelViewSet, basename='files-achannels')
files_router.register('dchannels', views.DigitalChannelViewSet, basename='files-dchannels')

urlpatterns += router.urls + projects_router.urls + files_router.urls

# END-POINTS
# -----------
# http://127.0.0.1:8000/comtrade_reader/projects/
# http://127.0.0.1:8000/comtrade_reader/projects/1/
# http://127.0.0.1:8000/comtrade_reader/projects/1/files/
# http://127.0.0.1:8000/comtrade_reader/projects/1/files/1/
# http://127.0.0.1:8000/comtrade_reader/afa-projects/dummy_1/
# http://127.0.0.1:8000/comtrade_reader/afa-projects-new/

# http://127.0.0.1:8000/comtrade_reader/files/  => no viewing
# http://127.0.0.1:8000/comtrade_reader/files/1/achannels/
# http://127.0.0.1:8000/comtrade_reader/files/1/dchannels/
# http://127.0.0.1:8000/comtrade_reader/files/1/achannels/1/
# http://127.0.0.1:8000/comtrade_reader/files/1/dchannels/1/

# http://127.0.0.1:8000/comtrade_reader/files/1/asignals/
# http://127.0.0.1:8000/comtrade_reader/files/1/dsignals/

# http://127.0.0.1:8000/comtrade_reader/phasors/<file_id>/
# http://127.0.0.1:8000/comtrade_reader/harmonics/<file_id>/<start_sample>/<end_sample>/
# http://127.0.0.1:8000/comtrade_reader/asignals/<file_id>/
# http://127.0.0.1:8000/comtrade_reader/dsignals/<file_id>/
# http://127.0.0.1:8000/comtrade_reader/resample/<file_id>/<new_sampling_rate>/<old_sampling_rate>/