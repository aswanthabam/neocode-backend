from django.shortcuts import render
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import (
    DocumentCategory, Document, DocumentAccess, DocumentAccessLog,
    DocumentShare, DocumentRequest
)
from .serializers import (
    DocumentCategorySerializer, DocumentCategoryCreateSerializer,
    DocumentSerializer, DocumentCreateSerializer, DocumentUpdateSerializer,
    DocumentAccessSerializer, DocumentAccessCreateSerializer,
    DocumentAccessLogSerializer, DocumentShareSerializer,
    DocumentShareCreateSerializer, DocumentRequestSerializer,
    DocumentRequestCreateSerializer, DocumentRequestResponseSerializer,
    DocumentStatsSerializer, DocumentSearchSerializer,
    DocumentBulkActionSerializer, DocumentVersionSerializer
)
from auth_api.models import UserActivity


class DocumentCategoryViewSet(viewsets.ModelViewSet):
    """Document category management"""
    queryset = DocumentCategory.objects.filter(is_active=True)
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCategoryCreateSerializer
        return DocumentCategorySerializer
    
    @extend_schema(
        summary="List document categories",
        description="Get list of all available document categories"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create document category",
        description="Create a new document category"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class DocumentViewSet(viewsets.ModelViewSet):
    """Document management"""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'trust_level', 'status', 'owner', 'created_at']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title', 'file_size']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        # Users can see their own documents and documents shared with them
        return Document.objects.filter(
            Q(owner=user) | Q(access_permissions__user=user)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DocumentUpdateSerializer
        return DocumentSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='document_uploaded',
            description=f'Uploaded document: {serializer.instance.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        serializer.save()
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='document_updated',
            description=f'Updated document: {serializer.instance.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        # Log activity before deletion
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='document_deleted',
            description=f'Deleted document: {instance.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        instance.delete()
    
    @extend_schema(
        summary="List documents",
        description="Get list of user's documents with filtering and search options",
        parameters=[
            OpenApiParameter(name='category', description='Filter by category', required=False, type=int),
            OpenApiParameter(name='trust_level', description='Filter by trust level', required=False, type=str),
            OpenApiParameter(name='status', description='Filter by status', required=False, type=str),
            OpenApiParameter(name='search', description='Search in title and description', required=False, type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Upload document",
        description="Upload new document with encryption and metadata"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get document details",
        description="Retrieve detailed information about specific document"
    )
    def retrieve(self, request, *args, **kwargs):
        # Log document view
        instance = self.get_object()
        DocumentAccessLog.objects.create(
            document=instance,
            user=request.user,
            action='view',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update document",
        description="Update document metadata and properties"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete document",
        description="Permanently delete document from vault"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Download document",
        description="Download document file"
    )
    def download(self, request, pk=None):
        document = self.get_object()
        
        # Log download
        DocumentAccessLog.objects.create(
            document=document,
            user=request.user,
            action='download',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return file response
        from django.http import FileResponse
        response = FileResponse(document.file, as_attachment=True, filename=document.original_filename)
        return response
    
    @action(detail=False, methods=['post'])
    @extend_schema(
        summary="Bulk actions",
        description="Perform bulk actions on documents"
    )
    def bulk_action(self, request):
        serializer = DocumentBulkActionSerializer(data=request.data)
        if serializer.is_valid():
            document_ids = serializer.validated_data['document_ids']
            action = serializer.validated_data['action']
            
            documents = Document.objects.filter(
                id__in=document_ids, 
                owner=request.user
            )
            
            if action == 'delete':
                documents.delete()
                message = f'Deleted {documents.count()} documents'
            elif action == 'archive':
                documents.update(status='archived')
                message = f'Archived {documents.count()} documents'
            elif action == 'share':
                target_user_id = serializer.validated_data.get('target_user')
                permission = serializer.validated_data.get('permission', 'view')
                if target_user_id:
                    target_user = CustomUser.objects.get(id=target_user_id)
                    for doc in documents:
                        DocumentShare.objects.create(
                            document=doc,
                            shared_by=request.user,
                            shared_with=target_user,
                            permission=permission
                        )
                    message = f'Shared {documents.count()} documents'
            
            return Response({'message': message})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    @extend_schema(
        summary="Document statistics",
        description="Get document statistics and analytics"
    )
    def stats(self, request):
        user = request.user
        
        # Calculate statistics
        total_documents = Document.objects.filter(owner=user).count()
        total_size = Document.objects.filter(owner=user).aggregate(
            total=Sum('file_size')
        )['total'] or 0
        
        documents_by_category = Document.objects.filter(owner=user).values(
            'category__name'
        ).annotate(count=Count('id'))
        
        documents_by_trust_level = Document.objects.filter(owner=user).values(
            'trust_level'
        ).annotate(count=Count('id'))
        
        recent_uploads = Document.objects.filter(owner=user).order_by('-created_at')[:5]
        most_viewed = Document.objects.filter(owner=user).order_by('-access_logs__count')[:5]
        most_downloaded = Document.objects.filter(owner=user).order_by('-access_logs__count')[:5]
        
        stats = {
            'total_documents': total_documents,
            'total_size': total_size,
            'documents_by_category': list(documents_by_category),
            'documents_by_trust_level': list(documents_by_trust_level),
            'recent_uploads': DocumentSerializer(recent_uploads, many=True).data,
            'most_viewed': DocumentSerializer(most_viewed, many=True).data,
            'most_downloaded': DocumentSerializer(most_downloaded, many=True).data,
        }
        
        serializer = DocumentStatsSerializer(stats)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DocumentAccessViewSet(viewsets.ModelViewSet):
    """Document access management"""
    serializer_class = DocumentAccessSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return DocumentAccess.objects.filter(
            Q(document__owner=user) | Q(user=user)
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentAccessCreateSerializer
        return DocumentAccessSerializer
    
    def perform_create(self, serializer):
        serializer.save(granted_by=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='access_granted',
            description=f'Granted access to document: {serializer.instance.document.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DocumentAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Document access log view"""
    serializer_class = DocumentAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'user', 'action', 'accessed_at']
    ordering = ['-accessed_at']
    
    def get_queryset(self):
        user = self.request.user
        return DocumentAccessLog.objects.filter(
            Q(document__owner=user) | Q(user=user)
        )


class DocumentShareViewSet(viewsets.ModelViewSet):
    """Document sharing management"""
    serializer_class = DocumentShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'permission', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        return DocumentShare.objects.filter(
            Q(shared_by=user) | Q(shared_with=user)
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentShareCreateSerializer
        return DocumentShareSerializer
    
    def perform_create(self, serializer):
        serializer.save(shared_by=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='document_shared',
            description=f'Shared document: {serializer.instance.document.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        share = self.get_object()
        if share.shared_with == request.user:
            share.status = 'accepted'
            share.save()
            return Response({'message': 'Share accepted'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        share = self.get_object()
        if share.shared_with == request.user:
            share.status = 'declined'
            share.save()
            return Response({'message': 'Share declined'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DocumentRequestViewSet(viewsets.ModelViewSet):
    """Document request management"""
    serializer_class = DocumentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        return DocumentRequest.objects.filter(
            Q(requester=user) | Q(requestee=user)
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DocumentRequestResponseSerializer
        return DocumentRequestSerializer
    
    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='document_requested',
            description=f'Requested document: {serializer.instance.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        serializer.save()
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='request_responded',
            description=f'Responded to document request: {serializer.instance.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        doc_request = self.get_object()
        if doc_request.requestee == request.user:
            doc_request.status = 'approved'
            doc_request.responded_at = timezone.now()
            doc_request.save()
            return Response({'message': 'Request approved'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        doc_request = self.get_object()
        if doc_request.requestee == request.user:
            doc_request.status = 'declined'
            doc_request.responded_at = timezone.now()
            doc_request.save()
            return Response({'message': 'Request declined'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DocumentIssueView(APIView):
    """Organization-issued documents directly to user's vault"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Issue document",
        description="Organization-issued documents directly to user's vault",
        request=DocumentCreateSerializer,
        responses={201: DocumentSerializer}
    )
    def post(self, request):
        # Check if user has organization profile with document issuance capability
        try:
            organization = request.user.organization_profile
            if not organization.can_issue_documents:
                return Response(
                    {'error': 'Organization does not have document issuance capability'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except:
            return Response(
                {'error': 'User does not have organization profile'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DocumentCreateSerializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save(
                owner=request.data.get('target_user'),
                issuer=request.user,
                issue_date=timezone.now(),
                trust_level='officially_issued'
            )
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='document_issued',
                description=f'Issued document: {document.title}',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
