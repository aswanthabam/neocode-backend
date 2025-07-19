from django.shortcuts import render
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import (
    QRCodeShare, ShareSession, SharingActivity, DocumentRequestResponse,
    ShareNotification
)
from .serializers import (
    QRCodeShareSerializer, QRCodeShareCreateSerializer,
    ShareSessionSerializer, ShareSessionCreateSerializer,
    SharingActivitySerializer, DocumentRequestResponseSerializer,
    DocumentRequestResponseCreateSerializer, ShareNotificationSerializer,
    ShareNotificationUpdateSerializer, QRCodeAccessSerializer,
    DocumentAccessViaQRSerializer, ShareStatsSerializer,
    BulkShareSerializer, QRCodeBulkCreateSerializer,
    ShareActivityFilterSerializer
)
from documents.models import Document, DocumentRequest
from auth_api.models import UserActivity


class QRCodeShareViewSet(viewsets.ModelViewSet):
    """QR code sharing management"""
    serializer_class = QRCodeShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'permission', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return QRCodeShare.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QRCodeShareCreateSerializer
        return QRCodeShareSerializer
    
    def perform_create(self, serializer):
        qr_share = serializer.save(created_by=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='qr_created',
            description=f'Created QR code for document: {qr_share.document.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        # Log activity before deletion
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='qr_revoked',
            description=f'Revoked QR code for document: {instance.document.title}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        instance.delete()
    
    @extend_schema(
        summary="List QR code shares",
        description="Get list of created QR code shares"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create QR code share",
        description="Generate QR code for temporary document sharing"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Revoke QR code",
        description="Revoke QR code share"
    )
    def revoke(self, request, pk=None):
        qr_share = self.get_object()
        qr_share.status = 'revoked'
        qr_share.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='qr_revoked',
            description=f'Revoked QR code for document: {qr_share.document.title}',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'QR code revoked'})
    
    @action(detail=False, methods=['post'])
    @extend_schema(
        summary="Bulk create QR codes",
        description="Create multiple QR codes for documents"
    )
    def bulk_create(self, request):
        serializer = QRCodeBulkCreateSerializer(data=request.data)
        if serializer.is_valid():
            document_ids = serializer.validated_data['document_ids']
            documents = Document.objects.filter(
                id__in=document_ids, 
                owner=request.user
            )
            
            created_qr_shares = []
            for document in documents:
                qr_share = QRCodeShare.objects.create(
                    document=document,
                    created_by=request.user,
                    title=serializer.validated_data['title'],
                    description=serializer.validated_data.get('description', ''),
                    permission=serializer.validated_data['permission'],
                    expires_at=serializer.validated_data['expires_at'],
                    max_views=serializer.validated_data['max_views']
                )
                created_qr_shares.append(qr_share)
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='qr_bulk_created',
                description=f'Created {len(created_qr_shares)} QR codes',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'message': f'Created {len(created_qr_shares)} QR codes',
                'qr_shares': QRCodeShareSerializer(created_qr_shares, many=True).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ShareSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Share session management"""
    serializer_class = ShareSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'accessed_at']
    ordering = ['-accessed_at']
    
    def get_queryset(self):
        return ShareSession.objects.filter(qr_share__created_by=self.request.user)
    
    @extend_schema(
        summary="List share sessions",
        description="Get list of QR code access sessions"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SharingActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Sharing activity management"""
    serializer_class = SharingActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity_type', 'created_at', 'user', 'document']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return SharingActivity.objects.filter(
            Q(user=user) | Q(document__owner=user)
        )
    
    @extend_schema(
        summary="List sharing activities",
        description="Get list of all sharing activities for audit trail",
        parameters=[
            OpenApiParameter(name='activity_type', description='Filter by activity type', required=False, type=str),
            OpenApiParameter(name='date_from', description='Filter from date', required=False, type=str),
            OpenApiParameter(name='date_to', description='Filter to date', required=False, type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DocumentRequestResponseViewSet(viewsets.ModelViewSet):
    """Document request response management"""
    serializer_class = DocumentRequestResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return DocumentRequestResponse.objects.filter(
            Q(responder=user) | Q(request__requester=user)
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentRequestResponseCreateSerializer
        return DocumentRequestResponseSerializer
    
    def perform_create(self, serializer):
        response = serializer.save(responder=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='request_responded',
            description=f'Responded to document request: {response.request.title}',
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


class ShareNotificationViewSet(viewsets.ModelViewSet):
    """Share notification management"""
    serializer_class = ShareNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'is_read', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ShareNotification.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ShareNotificationUpdateSerializer
        return ShareNotificationSerializer
    
    @action(detail=False, methods=['post'])
    @extend_schema(
        summary="Mark all as read",
        description="Mark all notifications as read"
    )
    def mark_all_read(self, request):
        ShareNotification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Mark as read",
        description="Mark specific notification as read"
    )
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})


class QRCodeAccessView(APIView):
    """Access shared documents via QR code"""
    permission_classes = []  # Public endpoint
    
    @extend_schema(
        summary="Access shared document",
        description="Access shared documents via session token (public endpoint)",
        request=QRCodeAccessSerializer,
        responses={200: DocumentAccessViaQRSerializer, 400: "Invalid QR code"}
    )
    def post(self, request):
        serializer = QRCodeAccessSerializer(data=request.data)
        if serializer.is_valid():
            qr_share_id = serializer.validated_data['qr_share_id']
            session_token = serializer.validated_data.get('session_token')
            
            try:
                qr_share = QRCodeShare.objects.get(id=qr_share_id)
                
                if not qr_share.is_active:
                    return Response(
                        {'error': 'QR code is no longer active'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create or get session
                if session_token:
                    try:
                        session = ShareSession.objects.get(
                            session_token=session_token,
                            qr_share=qr_share,
                            status='active'
                        )
                        if session.is_expired:
                            session.status = 'expired'
                            session.save()
                            return Response(
                                {'error': 'Session expired'}, 
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    except ShareSession.DoesNotExist:
                        return Response(
                            {'error': 'Invalid session token'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    # Create new session
                    session_serializer = ShareSessionCreateSerializer(data={'qr_share': qr_share.id})
                    if session_serializer.is_valid():
                        session = session_serializer.save()
                    else:
                        return Response(
                            session_serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Increment view count
                qr_share.current_views += 1
                qr_share.save()
                
                # Log activity
                SharingActivity.objects.create(
                    user=qr_share.created_by,
                    activity_type='qr_accessed',
                    document=qr_share.document,
                    qr_share=qr_share,
                    share_session=session,
                    description=f'QR code accessed for document: {qr_share.document.title}',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Return document access info
                access_data = {
                    'document_title': qr_share.document.title,
                    'document_description': qr_share.document.description or '',
                    'permission': qr_share.permission,
                    'expires_at': qr_share.expires_at,
                    'created_by_name': qr_share.created_by.full_name,
                    'access_url': f'/api/v1/sharing/access/{session.session_token}/',
                    'download_url': f'/api/v1/sharing/download/{session.session_token}/' if qr_share.permission == 'download' else None
                }
                
                return Response(access_data)
                
            except QRCodeShare.DoesNotExist:
                return Response(
                    {'error': 'Invalid QR code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ShareStatsView(APIView):
    """Sharing statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get sharing statistics",
        description="Get sharing statistics and analytics"
    )
    def get(self, request):
        user = request.user
        
        # Calculate statistics
        total_qr_shares = QRCodeShare.objects.filter(created_by=user).count()
        active_qr_shares = QRCodeShare.objects.filter(
            created_by=user, 
            status='active'
        ).exclude(expires_at__lt=timezone.now()).count()
        
        total_sessions = ShareSession.objects.filter(qr_share__created_by=user).count()
        active_sessions = ShareSession.objects.filter(
            qr_share__created_by=user, 
            status='active'
        ).exclude(expires_at__lt=timezone.now()).count()
        
        total_requests_sent = DocumentRequest.objects.filter(requester=user).count()
        total_requests_received = DocumentRequest.objects.filter(requestee=user).count()
        pending_requests = DocumentRequest.objects.filter(requestee=user, status='pending').count()
        
        total_notifications = ShareNotification.objects.filter(user=user).count()
        unread_notifications = ShareNotification.objects.filter(user=user, is_read=False).count()
        
        stats = {
            'total_qr_shares': total_qr_shares,
            'active_qr_shares': active_qr_shares,
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_requests_sent': total_requests_sent,
            'total_requests_received': total_requests_received,
            'pending_requests': pending_requests,
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
        }
        
        serializer = ShareStatsSerializer(stats)
        return Response(serializer.data)


class BulkShareView(APIView):
    """Bulk sharing operations"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Bulk share documents",
        description="Share multiple documents with users"
    )
    def post(self, request):
        serializer = BulkShareSerializer(data=request.data)
        if serializer.is_valid():
            document_ids = serializer.validated_data['document_ids']
            target_users = serializer.validated_data.get('target_users', [])
            permission = serializer.validated_data['permission']
            expires_at = serializer.validated_data.get('expires_at')
            message = serializer.validated_data.get('message', '')
            
            documents = Document.objects.filter(
                id__in=document_ids, 
                owner=request.user
            )
            
            shared_count = 0
            for document in documents:
                for user_id in target_users:
                    try:
                        target_user = CustomUser.objects.get(id=user_id)
                        DocumentShare.objects.create(
                            document=document,
                            shared_by=request.user,
                            shared_with=target_user,
                            permission=permission,
                            expires_at=expires_at,
                            message=message
                        )
                        shared_count += 1
                    except CustomUser.DoesNotExist:
                        continue
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='bulk_share',
                description=f'Bulk shared {shared_count} documents',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'message': f'Successfully shared {shared_count} documents',
                'shared_count': shared_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
