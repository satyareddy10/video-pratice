from django.urls import path
from .views import (
    InitiateUploadView, 
    GetPresignedUrlView,
    CompleteUploadView, 
    ListPartsView
)

urlpatterns = [
    path('upload/initiate/', InitiateUploadView.as_view(), name='initiate-upload'),
    path('upload/presigned-url/', GetPresignedUrlView.as_view(), name='get-presigned-url'),
    path('upload/complete/', CompleteUploadView.as_view(), name='complete-upload'),
    path('upload/parts/<uuid:video_id>/', ListPartsView.as_view(), name='list-parts'),
]
