from django.core.management.base import BaseCommand
from django.db import transaction
from sklearn.cluster import KMeans
import numpy as np
from accidents.models import Crash
from hotspots.models import Hotspot

class Command(BaseCommand):
    help = 'Generate accident hotspots using K-means clustering'
    
    def add_arguments(self, parser):
        parser.add_argument('--clusters', type=int, default=50, help='Number of hotspots to generate')
        parser.add_argument('--min-crashes', type=int, default=5, help='Minimum crashes per hotspot')
    
    def handle(self, *args, **options):
        n_clusters = options['clusters']
        min_crashes = options['min_crashes']
        
        # Get all crashes with coordinates
        crashes = Crash.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
            ).values('collision_id', 'latitude', 'longitude', 'number_of_persons_injured', 'number_of_persons_killed')        
        if len(crashes) < n_clusters:
            self.stdout.write(f"Not enough crashes ({len(crashes)}) for {n_clusters} clusters")
            return
        
        # Prepare data for clustering
        coordinates = np.array([[c['latitude'], c['longitude']] for c in crashes])
        
        # Run K-means clustering
        self.stdout.write(f"Running K-means clustering on {len(crashes)} crashes...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(coordinates)
        
        # Clear existing hotspots
        Hotspot.objects.all().delete()
        
        # Generate hotspots
        hotspots_created = 0
        for i in range(n_clusters):
            # Get crashes in this cluster
            cluster_crashes = [crashes[j] for j in range(len(crashes)) if cluster_labels[j] == i]
            
            if len(cluster_crashes) < min_crashes:
                continue
            
            # Calculate cluster center and statistics
            cluster_coords = np.array([[c['latitude'], c['longitude']] for c in cluster_crashes])
            center_lat = np.mean(cluster_coords[:, 0])
            center_lon = np.mean(cluster_coords[:, 1])
            
            # Calculate radius (distance from center to farthest point)
            distances = np.sqrt(np.sum((cluster_coords - [center_lat, center_lon])**2, axis=1))
            radius = np.max(distances) * 111000  # Convert to meters (rough approximation)
            
            # Calculate statistics
            total_injured = sum(c['number_of_persons_injured'] for c in cluster_crashes)
            total_killed = sum(c['number_of_persons_killed'] for c in cluster_crashes)
            crash_count = len(cluster_crashes)
            
            # Calculate severity index (crashes + injuries + 10*fatalities)
            severity_index = crash_count + total_injured + (total_killed * 10)
            # Create hotspot
            hotspot = Hotspot.objects.create(
                name=f"Hotspot {i+1}",
                latitude=center_lat,
                longitude=center_lon,
                radius=radius,
                crash_count=crash_count,
                total_injured=total_injured,
                total_killed=total_killed,
                severity_index=severity_index
            )
            
            hotspots_created += 1
            self.stdout.write(f"Created hotspot {i+1}: {crash_count} crashes, severity: {severity_index:.1f}")
        
        self.stdout.write(f"Generated {hotspots_created} hotspots from {len(crashes)} crashes")