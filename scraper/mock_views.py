from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
import io
import os
import logging

logger = logging.getLogger(__name__)

class MockAuthResourcesAPIView(APIView):
    """
    Mock API view to simulate the behavior of the AuthenticatedResourcesAPIView
    """
    def post(self, request):
        # Get the course URL, username, and password from the request data
        course_url = request.data.get('url')
        username = request.data.get('username')
        password = request.data.get('password')
        download_file = request.data.get('download_file', True)  # Default to True to download files
        
        logger.info(f"Received mock request for course URL: {course_url}")
        logger.info(f"Download file flag: {download_file}")

        if not course_url:
            return Response({
                'status': 'error',
                'message': 'Course URL is required in the request body'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not username or not password:
            return Response({
                'status': 'error',
                'message': 'Username and password are required for authentication'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Simulate authentication
        if username != 'yakoub.benaissa' or password != 'aLnmftOM':
            return Response({
                'status': 'error',
                'message': 'Authentication failed. Please check your credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Simulate resource extraction
        resources = [
            {
                'resource_name': 'Techniques d\'Analyse Physico-chimique II',
                'resource_url': 'https://elearning.univ-bba.dz/mod/resource/view.php?id=131855',
                'pdf_url': 'https://elearning.univ-bba.dz/pluginfile.php/123456/mod_resource/content/1/Techniques_Analyse.docx',
                'pdf_name': 'Techniques_Analyse.docx'
            },
            {
                'resource_name': 'Techniques d\'Analyse Physico-chimique II TD2',
                'resource_url': 'https://elearning.univ-bba.dz/mod/resource/view.php?id=131856',
                'pdf_url': 'https://elearning.univ-bba.dz/pluginfile.php/123457/mod_resource/content/1/TD_Corrige.docx',
                'pdf_name': 'TD_Corrige.docx'
            }
        ]

        # Check if we should download the file
        if download_file:
            # Get the first resource
            resource = resources[0]
            
            # Create a mock file
            file_content = io.BytesIO(b'This is a mock file content for testing purposes.')
            
            # Return the file
            filename = resource['pdf_name']
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            
            response = FileResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        # If download_file is False, return the JSON response
        return Response({
            'status': 'success',
            'course_url': course_url,
            'authenticated': True,
            'count': len(resources),
            'data': resources
        }, status=status.HTTP_200_OK)
