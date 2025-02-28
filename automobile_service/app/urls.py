from django.urls import path
from .views import (
    ListPartsView,
    UploadFileView,
    DownloadSingleFileView,
    DownloadAllFilesForPartView,
    DownloadAllFilesForAutomobileView, ListAutomobilesView, GetAutomobileView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('automobiles/<int:automobile_id>/parts/', ListPartsView.as_view(), name='list_parts'),
    path('automobiles/<int:automobile_id>/parts/<int:part_id>/upload/', UploadFileView.as_view(), name='upload_file'),
    path('automobiles/<int:automobile_id>/download_all/', DownloadAllFilesForAutomobileView.as_view(), name='download_all_files_for_automobile'),
    path('automobiles/', ListAutomobilesView.as_view(), name ='list_automobiles'),
    path('automobiles/<str:pk>/', GetAutomobileView.as_view(), name='get_automobile'),
    path('parts/<int:part_id>/files/<int:file_id>/download/', DownloadSingleFileView.as_view(), name='download_single_file'),
    path('parts/<int:part_id>/download_all/', DownloadAllFilesForPartView.as_view(), name='download_all_files_for_part'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
