from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Hotspot

class HotspotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hotspot.objects.all()
    
    def get_serializer_class(self):
        # Since we're not using serializers, we'll handle serialization manually
        return None
    
    def list(self, request):
        """List hotspots with basic info"""
        hotspots = self.get_queryset()
        return Response([{
            'id': h.id,
            'name': h.name,
            'latitude': h.latitude,
            'longitude': h.longitude,
            'radius': h.radius,
            'crash_count': h.crash_count,
            'total_injured': h.total_injured,
            'total_killed': h.total_killed,
            'severity_index': h.severity_index
        } for h in hotspots])
    
    def retrieve(self, request, pk=None):
        """Get detailed hotspot info"""
        try:
            hotspot = Hotspot.objects.get(id=pk)
            return Response({
                'id': hotspot.id,
                'name': hotspot.name,
                'latitude': hotspot.latitude,
                'longitude': hotspot.longitude,
                'radius': hotspot.radius,
                'crash_count': hotspot.crash_count,
                'total_injured': hotspot.total_injured,
                'total_killed': hotspot.total_killed,
                'severity_index': hotspot.severity_index,
                'created_at': hotspot.created_at
            })
        except Hotspot.DoesNotExist:
            return Response({'error': 'Hotspot not found'}, status=404)
    
    def get_queryset(self):
        queryset = Hotspot.objects.all()
        
        # Filter by minimum crash count
        min_crashes = self.request.query_params.get('min_crashes')
        if min_crashes:
            queryset = queryset.filter(crash_count__gte=int(min_crashes))
        
        # Filter by severity
        min_severity = self.request.query_params.get('min_severity')
        if min_severity:
            queryset = queryset.filter(severity_index__gte=float(min_severity))
        
        return queryset.order_by('-severity_index')
    
    @action(detail=False, methods=['get'])
    def top_severity(self, request):
        """Get top N hotspots by severity"""
        limit = int(request.query_params.get('limit', 10))
        hotspots = self.get_queryset()[:limit]
        return Response([{
            'id': h.id,
            'name': h.name,
            'latitude': h.latitude,
            'longitude': h.longitude,
            'radius': h.radius,
            'crash_count': h.crash_count,
            'total_injured': h.total_injured,
            'total_killed': h.total_killed,
            'severity_index': h.severity_index
        } for h in hotspots])
