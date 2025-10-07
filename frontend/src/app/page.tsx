import { api } from '@/lib/api';
import Map from '@/components/Map';

export default async function Home() {
  // Fetch data from your Django API
  const [crashStats, hotspots] = await Promise.all([
    api.crashes.getStats(),
    api.hotspots.getAll()
  ]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          NYC Traffic Accident Explorer
        </h1>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700">Total Crashes</h3>
            <p className="text-3xl font-bold text-blue-600">{crashStats.total_crashes}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700">Total Injured</h3>
            <p className="text-3xl font-bold text-orange-600">{crashStats.total_injured}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700">Total Killed</h3>
            <p className="text-3xl font-bold text-red-600">{crashStats.total_killed}</p>
          </div>
        </div>
        
        {/* Interactive Map */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Accident Hotspots Map</h2>
          <Map hotspots={hotspots} />
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