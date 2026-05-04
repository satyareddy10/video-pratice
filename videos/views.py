from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Video
from .utils import S3Service
import os
import uuid

class InitiateUploadView(APIView):
    def post(self, request):
        filename = request.data.get('filename')
        content_type = request.data.get('content_type', 'video/mp4')
        title = request.data.get('title', filename)
        file_size = request.data.get('file_size')
        
        if not filename or not file_size:
            return Response({'error': 'Filename and file_size are required'}, status=status.HTTP_400_BAD_REQUEST)

        # 100MB chunks
        chunk_size = 100 * 1024 * 1024
        total_parts = (int(file_size) + chunk_size - 1) // chunk_size

        video_id = uuid.uuid4()
        s3_key = f"uploads/raw/{str(request.user.id)}/{str(video_id)}/{filename}"
        
        s3 = S3Service()
        try:
            upload_id = s3.initiate_multipart_upload(s3_key, content_type)
            
            video = Video.objects.create(
                id=video_id,
                user=request.user,
                title=title,
                filename=filename,
                file_size=int(file_size),
                s3_key=s3_key,
                upload_id=upload_id,
                status='uploading'
            )

            urls = []
            for part_number in range(1, total_parts + 1):
                url = s3.generate_presigned_url(s3_key, upload_id, part_number)
                urls.append({
                    'part_number': part_number,
                    'url': url
                })
            
            return Response({
                'video_id': video.id,
                'upload_id': upload_id,
                'key': s3_key,
                'urls': urls,
                'chunk_size': chunk_size
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPresignedUrlView(APIView):
    def post(self, request):
        video_id = request.data.get('video_id')
        part_number = request.data.get('part_number')
        
        try:
            video = Video.objects.get(id=video_id, user=request.user)
            s3 = S3Service()
            url = s3.generate_presigned_url(video.s3_key, video.upload_id, part_number)
            return Response({'url': url})
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompleteUploadView(APIView):
    def post(self, request):
        video_id = request.data.get('video_id')
        parts = request.data.get('parts') # List of {'ETag': ..., 'PartNumber': ...}
        
        try:
            video = Video.objects.get(id=video_id, user=request.user)
            s3 = S3Service()
            s3.complete_multipart_upload(video.s3_key, video.upload_id, parts)
            
            video.status = 'completed'
            video.save()
            
            return Response({'status': 'completed'})
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            video.status = 'failed'
            video.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListPartsView(APIView):
    def get(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id, user=request.user)
            s3 = S3Service()
            parts = s3.list_parts(video.s3_key, video.upload_id)
            return Response({'parts': parts})
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
