'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Map from '@/components/Map';
import FilterPanel from '@/components/FilterPanel';

interface CrashStats {
  total_crashes: number;
  total_injured: number;
  total_killed: number;
  borough_breakdown: any[];
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
  vehicle_type_code1: string;
  vehicle_type_code2: string;
  vehicle_type_code_3: string;
  vehicle_type_code_4: string;
  vehicle_type_code_5: string;
}

export default function Home() {
  const [crashStats, setCrashStats] = useState<CrashStats | null>(null);
  const [hotspots, setHotspots] = useState([]);
  const [crashes, setCrashes] = useState<Crash[]>([]);
  const [allCrashes, setAllCrashes] = useState<Crash[]>([]); // Store original data
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(true);

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, hotspotsData, crashesData] = await Promise.all([
          api.crashes.getStats(),
          api.hotspots.getAll(),
          api.crashes.getAll()
        ]);
        setCrashStats(statsData);
        setHotspots(hotspotsData);
        setCrashes(crashesData);
        setAllCrashes(crashesData); // Store original data
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

// Apply filters
const applyFilters = (newFilters: any) => {
  setFilters(newFilters);
  
  // Filter data based on new filters
  const filteredCrashes = allCrashes.filter(crash => {
    // Borough filter
    if (newFilters.borough && crash.borough !== newFilters.borough) {
      return false;
    }
    
    // Date range filters
    if (newFilters.startDate && new Date(crash.crash_date) < new Date(newFilters.startDate)) {
      return false;
    }
    if (newFilters.endDate && new Date(crash.crash_date) > new Date(newFilters.endDate)) {
      return false;
    }
    
    // Severity filter (using total_severity property from backend)
    if (newFilters.minSeverity && crash.total_severity < parseInt(newFilters.minSeverity)) {
      return false;
    }
    
    // Vehicle type filter (check vehicle_type_code fields)
    if (newFilters.vehicleType) {
      const vehicleTypes = [
        crash.vehicle_type_code1,
        crash.vehicle_type_code2,
        crash.vehicle_type_code_3,
        crash.vehicle_type_code_4,
        crash.vehicle_type_code_5
      ].filter(Boolean);
      
      const hasMatchingVehicle = vehicleTypes.some(vt => 
        vt && vt.toLowerCase().includes(newFilters.vehicleType.toLowerCase())
      );
      
      if (!hasMatchingVehicle) {
        return false;
      }
    }
    
    // Fatalities filter - FIXED LOGIC
    if (newFilters.showFatalities && crash.number_of_persons_killed === 0) {
      return false;
    }
    
    // Injuries filter - FIXED LOGIC  
    if (newFilters.showInjuries && crash.number_of_persons_injured === 0) {
      return false;
    }
    
    return true;
  });

  // Update crashes state with filtered data
  setCrashes(filteredCrashes);
  
  // Recalculate stats based on filtered data
  const newStats = {
    total_crashes: filteredCrashes.length,
    total_injured: filteredCrashes.reduce((sum, crash) => sum + crash.number_of_persons_injured, 0),
    total_killed: filteredCrashes.reduce((sum, crash) => sum + crash.number_of_persons_killed, 0),
    borough_breakdown: []
  };
  setCrashStats(newStats);
};

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading NYC Traffic Data...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          NYC Traffic Accident Explorer
        </h1>
        
        {/* Filter Panel */}
        <div className="mb-8">
          <FilterPanel onFiltersChange={applyFilters} />
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700">Total Crashes</h3>
            <p className="text-3xl font-bold text-blue-600">{crashStats?.total_crashes}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700">Total Injured</h3>
            <p className="text-3xl font-bold text-orange-600">{crashStats?.total_injured}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700">Total Killed</h3>
            <p className="text-3xl font-bold text-red-600">{crashStats?.total_killed}</p>
          </div>
        </div>
        
        {/* Interactive Map */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Accident Hotspots Map</h2>
            <div className="text-sm text-gray-600">
              {crashes.length > 0 ? (
                <span>Showing severity hotspots (≥5 crashes, 1.5km radius) - {crashes.length} crashes analyzed</span>
              ) : (
                <span>No crashes match current filters</span>
              )}
            </div>
          </div>
          <Map hotspots={hotspots} crashes={crashes} filters={filters} />
          
          {/* Severity Legend */}
          <div className="mt-4 bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Severity Legend</h3>
            <div className="flex flex-wrap gap-4 text-xs">
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-gray-800 mr-2"></div>
                <span>Critical (2+)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-red-600 mr-2"></div>
                <span>High (1-2)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-orange-600 mr-2"></div>
                <span>Medium-High (0.5-1)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-orange-500 mr-2"></div>
                <span>Medium (0.2-0.5)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-yellow-500 mr-2"></div>
                <span>Low (0.05-0.2)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-green-300 mr-2"></div>
                <span>Very Low (&lt;0.05)</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Hotspots List */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Accident Hotspots</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {hotspots.slice(0, 6).map((hotspot: any) => (
              <div key={hotspot.id} className="border p-4 rounded-lg">
                <h3 className="font-semibold">{hotspot.name}</h3>
                <p className="text-sm text-gray-600">
                  {hotspot.crash_count} crashes, {hotspot.total_injured} injured
                </p>
                <p className="text-sm font-medium text-red-600">
                  Severity: {hotspot.severity_index}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}