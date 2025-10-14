'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface Hotspot {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  crash_count: number;
  total_injured: number;
  total_killed: number;
  severity_index: number;
}

interface Crash {
  collision_id: number;
  crash_date: string;
  latitude: number;
  longitude: number;
  borough: string;
  number_of_persons_injured: number;
  number_of_persons_killed: number;
  total_severity: number;
}

interface MapProps {
  hotspots: Hotspot[];
  crashes: Crash[];
  filters: any;
}

// Helper function to create severity-based hotspots from crashes
const createSeverityHotspots = (crashes: Crash[]) => {
  const hotspots: any[] = [];
  const processedCrashes = new Set<number>();
  
  crashes.forEach((crash, index) => {
    if (processedCrashes.has(crash.collision_id)) return;
    
    const nearbyCrashes = crashes.filter(otherCrash => {
      if (processedCrashes.has(otherCrash.collision_id)) return false;
      
      // Calculate distance (rough approximation)
      const latDiff = Math.abs(crash.latitude - otherCrash.latitude);
      const lonDiff = Math.abs(crash.longitude - otherCrash.longitude);
      const distance = Math.sqrt(latDiff * latDiff + lonDiff * lonDiff);
      
      return distance < 0.015; // ~1.5km radius - larger grouping for readability
    });
    
    // Group nearby crashes into a hotspot
    const totalInjured = nearbyCrashes.reduce((sum, c) => sum + c.number_of_persons_injured, 0);
    const totalKilled = nearbyCrashes.reduce((sum, c) => sum + c.number_of_persons_killed, 0);
    const avgSeverity = nearbyCrashes.reduce((sum, c) => sum + c.total_severity, 0) / nearbyCrashes.length;
    
    hotspots.push({
      longitude: crash.longitude,
      latitude: crash.latitude,
      crashCount: nearbyCrashes.length,
      totalInjured,
      totalKilled,
      avgSeverity,
      borough: crash.borough
    });
    
    // Mark these crashes as processed
    nearbyCrashes.forEach(c => processedCrashes.add(c.collision_id));
  });
  
  return hotspots;
};

// Helper function to get color based on severity (weather radar style)
const getSeverityColor = (severity: number) => {
  if (severity >= 2) return 'rgba(139, 0, 0, 0.8)'; // Dark red - critical
  if (severity >= 1) return 'rgba(220, 20, 60, 0.8)'; // Crimson - high
  if (severity >= 0.5) return 'rgba(255, 69, 0, 0.8)'; // Orange red - medium-high
  if (severity >= 0.2) return 'rgba(255, 140, 0, 0.8)'; // Dark orange - medium
  if (severity >= 0.1) return 'rgba(255, 165, 0, 0.8)';  // Orange - low-medium
  if (severity >= 0.05) return 'rgba(255, 215, 0, 0.8)';  // Gold - low
  return 'rgba(144, 238, 144, 0.8)'; // Light green - very low
};

export default function Map({ hotspots, crashes, filters }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [markers, setMarkers] = useState<mapboxgl.Marker[]>([]);

  useEffect(() => {
    if (map.current) return; // Initialize map only once

    mapboxgl.accessToken = 'pk.eyJ1Ijoicm9uYmhhIiwiYSI6ImNtZ2c4eGQ1ZDA0MGIybXB5MW14Nm1oa2QifQ.s5UKRp3-pk4mYCllpyK6mg';

    map.current = new mapboxgl.Map({
      container: mapContainer.current!,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-73.935242, 40.730610], // NYC coordinates
      zoom: 10
    });
  }, []);

  // Filter and display markers
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markers.forEach(marker => marker.remove());
    const newMarkers: mapboxgl.Marker[] = [];

    // Skip backend hotspots - we'll use our custom severity circles instead

    // Create severity-based hotspot circles from filtered crashes
    if (crashes.length > 0) {
      // Group crashes by proximity and calculate severity
      const hotspots = createSeverityHotspots(crashes);
      
      // Debug: Log severity distribution
      const severityRanges = {
        critical: hotspots.filter(h => h.avgSeverity >= 100).length,
        high: hotspots.filter(h => h.avgSeverity >= 50 && h.avgSeverity < 100).length,
        mediumHigh: hotspots.filter(h => h.avgSeverity >= 25 && h.avgSeverity < 50).length,
        medium: hotspots.filter(h => h.avgSeverity >= 10 && h.avgSeverity < 25).length,
        low: hotspots.filter(h => h.avgSeverity >= 1 && h.avgSeverity < 10).length,
        veryLow: hotspots.filter(h => h.avgSeverity < 1).length
      };
      console.log('Hotspot severity distribution:', severityRanges);
      console.log('Sample severities:', hotspots.slice(0, 5).map(h => h.avgSeverity));
      
      hotspots.forEach((hotspot) => {
        // Only show hotspots with at least 5 crashes for readability
        if (hotspot.crashCount < 5) return;
        
        // Color based on severity (like weather radar)
        const color = getSeverityColor(hotspot.avgSeverity);
        // Size based on severity and crash count (more emphasis on severity)
        const severitySize = hotspot.avgSeverity * 20; // Scale severity for size
        const countSize = Math.log(hotspot.crashCount) * 8; // Log scale for crash count
        const size = Math.min(60, Math.max(15, severitySize + countSize));
        
        // Create custom marker element
        const el = document.createElement('div');
        el.style.width = `${size}px`;
        el.style.height = `${size}px`;
        el.style.borderRadius = '50%';
        el.style.backgroundColor = color;
        el.style.cursor = 'pointer';
        el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
        
        const marker = new mapboxgl.Marker(el)
          .setLngLat([hotspot.longitude, hotspot.latitude])
          .setPopup(
            new mapboxgl.Popup({ offset: 25 })
              .setHTML(`
                <div class="p-3" style="color: #1f2937; font-family: system-ui, sans-serif;">
                  <h3 class="font-bold text-lg mb-2" style="color: #111827;">Crash Hotspot</h3>
                  <p class="mb-1"><strong>Crashes:</strong> ${hotspot.crashCount}</p>
                  <p class="mb-1"><strong>Total Injured:</strong> ${hotspot.totalInjured}</p>
                  <p class="mb-1"><strong>Total Killed:</strong> ${hotspot.totalKilled}</p>
                  <p class="mb-1"><strong>Avg Severity:</strong> ${hotspot.avgSeverity.toFixed(2)}</p>
                  <p class="mb-0"><strong>Borough:</strong> ${hotspot.borough}</p>
                </div>
              `)
          )
          .addTo(map.current!);
        
        newMarkers.push(marker);
      });
    }

    setMarkers(newMarkers);
  }, [hotspots, crashes, filters]);

  return (
    <div className="w-full h-96 rounded-lg overflow-hidden shadow-lg">
      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
}