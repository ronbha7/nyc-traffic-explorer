from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Crash

class CrashViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Crash.objects.all()
    
    def list(self, request):
        """List crashes with basic info"""
        crashes = self.get_queryset()
        return Response([{
            'collision_id': c.collision_id,
            'crash_date': c.crash_date,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'borough': c.borough,
            'number_of_persons_injured': c.number_of_persons_injured,
            'number_of_persons_killed': c.number_of_persons_killed,
            'total_severity': c.total_severity
        } for c in crashes])
    
    def retrieve(self, request, pk=None):
        """Get detailed crash info"""
        try:
            crash = Crash.objects.get(collision_id=pk)
            return Response({
                'collision_id': crash.collision_id,
                'crash_date': crash.crash_date,
                'crash_time': crash.crash_time,
                'latitude': crash.latitude,
                'longitude': crash.longitude,
                'borough': crash.borough,
                'zip_code': crash.zip_code,
                'on_street_name': crash.on_street_name,
                'cross_street_name': crash.cross_street_name,
                'off_street_name': crash.off_street_name,
                'number_of_persons_injured': crash.number_of_persons_injured,
                'number_of_persons_killed': crash.number_of_persons_killed,
                'number_of_pedestrians_injured': crash.number_of_pedestrians_injured,
                'number_of_pedestrians_killed': crash.number_of_pedestrians_killed,
                'number_of_cyclist_injured': crash.number_of_cyclist_injured,
                'number_of_cyclist_killed': crash.number_of_cyclist_killed,
                'number_of_motorist_injured': crash.number_of_motorist_injured,
                'number_of_motorist_killed': crash.number_of_motorist_killed,
                'contributing_factor_vehicle_1': crash.contributing_factor_vehicle_1,
                'contributing_factor_vehicle_2': crash.contributing_factor_vehicle_2,
                'vehicle_type_code1': crash.vehicle_type_code1,
                'vehicle_type_code2': crash.vehicle_type_code2,
                'total_severity': crash.total_severity
            })
        except Crash.DoesNotExist:
            return Response({'error': 'Crash not found'}, status=404)
    
    @action(detail=False, methods=['get'])
    def search_by_location(self, request):
        """Search crashes within a radius of given coordinates"""
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        radius = request.query_params.get('radius', 1000)
        
        if not lat or not lon:
            return Response({'error': 'Latitude and longitude are required'}, status=400)
        
        try:
            lat = float(lat)
            lon = float(lon)
            radius = float(radius)
        except ValueError:
            return Response({'error': 'Invalid coordinate values'}, status=400)
        
        # Simple radius search
        lat_delta = radius / 111000
        lon_delta = radius / (111000 * abs(lat / 90))
        
        crashes = Crash.objects.filter(
            latitude__gte=lat - lat_delta,
            latitude__lte=lat + lat_delta,
            longitude__gte=lon - lon_delta,
            longitude__lte=lon + lon_delta,
        )
        
        return Response({
            'count': crashes.count(),
            'results': [{
                'collision_id': c.collision_id,
                'crash_date': c.crash_date,
                'latitude': c.latitude,
                'longitude': c.longitude,
                'borough': c.borough,
                'total_severity': c.total_severity
            } for c in crashes]
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get crash statistics"""
        queryset = self.get_queryset()
        
        total_crashes = queryset.count()
        total_injured = queryset.aggregate(total=Sum('number_of_persons_injured'))['total'] or 0
        total_killed = queryset.aggregate(total=Sum('number_of_persons_killed'))['total'] or 0
        
        borough_stats = queryset.values('borough').annotate(
            crash_count=Count('collision_id'),
            injured_count=Sum('number_of_persons_injured'),
            killed_count=Sum('number_of_persons_killed')
        ).order_by('-crash_count')
        
        return Response({
            'total_crashes': total_crashes,
            'total_injured': total_injured,
            'total_killed': total_killed,
            'borough_breakdown': list(borough_stats)
        })