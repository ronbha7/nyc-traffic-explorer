'use client';

import { useEffect, useRef } from 'react';
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

interface MapProps {
  hotspots: Hotspot[];
}

export default function Map({ hotspots }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (map.current) return; // Initialize map only once

    // You'll need to get a free Mapbox token from https://mapbox.com
    mapboxgl.accessToken = 'pk.eyJ1Ijoicm9uYmhhIiwiYSI6ImNtZ2c4eGQ1ZDA0MGIybXB5MW14Nm1oa2QifQ.s5UKRp3-pk4mYCllpyK6mg';

    map.current = new mapboxgl.Map({
      container: mapContainer.current!,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-73.935242, 40.730610], // NYC coordinates
      zoom: 10
    });

    // Add markers for each hotspot
    hotspots.forEach((hotspot) => {
      // Color based on severity
      const color = hotspot.severity_index > 150 ? '#ef4444' : 
                   hotspot.severity_index > 100 ? '#f97316' : '#eab308';

      new mapboxgl.Marker({ color })
        .setLngLat([hotspot.longitude, hotspot.latitude])
        .setPopup(
          new mapboxgl.Popup({ offset: 25 })
            .setHTML(`
              <div class="p-2">
                <h3 class="font-bold">${hotspot.name}</h3>
                <p>Crashes: ${hotspot.crash_count}</p>
                <p>Injured: ${hotspot.total_injured}</p>
                <p>Killed: ${hotspot.total_killed}</p>
                <p class="font-semibold">Severity: ${hotspot.severity_index}</p>
              </div>
            `)
        )
        .addTo(map.current!);
    });
  }, [hotspots]);

  return (
    <div className="w-full h-96 rounded-lg overflow-hidden shadow-lg">
      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
}