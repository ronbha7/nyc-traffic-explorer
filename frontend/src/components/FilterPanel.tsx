
import { useState } from 'react';

interface FilterPanelProps {
  onFiltersChange: (filters: any) => void;
}

export default function FilterPanel({ onFiltersChange }: FilterPanelProps) {
  const [filters, setFilters] = useState({
    borough: '',
    startDate: '',
    endDate: '',
    minSeverity: '',
    vehicleType: '',
    showFatalities: false,
    showInjuries: false
  });

  const boroughs = [
    'MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND'
  ];

  const vehicleTypes = [
    'car/suv', 'truck/bus', 'motorcycle', 'bicycle', 'ebike', 'escooter'
  ];

  const handleFilterChange = (key: string, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = {
      borough: '',
      startDate: '',
      endDate: '',
      minSeverity: '',
      vehicleType: '',
      showFatalities: false,
      showInjuries: false
    };
    setFilters(emptyFilters);
    onFiltersChange(emptyFilters);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        <button
          onClick={clearFilters}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Borough Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-1">
            Borough
          </label>
          <select
            value={filters.borough}
            onChange={(e) => handleFilterChange('borough', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value="">All Boroughs</option>
            {boroughs.map(borough => (
              <option key={borough} value={borough}>{borough}</option>
            ))}
          </select>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-1">
            Start Date
          </label>
          <input
            type="date"
            value={filters.startDate}
            onChange={(e) => handleFilterChange('startDate', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-gray-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-900 mb-1">
            End Date
          </label>
          <input
            type="date"
            value={filters.endDate}
            onChange={(e) => handleFilterChange('endDate', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-gray-900"
          />
        </div>

        {/* Severity Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-1">
            Min Severity
          </label>
          <select
            value={filters.minSeverity}
            onChange={(e) => handleFilterChange('minSeverity', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value="">Any Severity</option>
            <option value="1">Injuries Only</option>
            <option value="10">Fatalities Only</option>
            <option value="5">Serious (5+ severity)</option>
            <option value="20">Critical (20+ severity)</option>
          </select>
        </div>

        {/* Vehicle Type */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-1">
            Vehicle Type
          </label>
          <select
            value={filters.vehicleType}
            onChange={(e) => handleFilterChange('vehicleType', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value="">All Vehicles</option>
            {vehicleTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        {/* Checkboxes */}
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.showFatalities}
              onChange={(e) => handleFilterChange('showFatalities', e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm text-gray-900">Fatalities Only</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.showInjuries}
              onChange={(e) => handleFilterChange('showInjuries', e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm text-gray-900">Injuries Only</span>
          </label>
        </div>
      </div>
    </div>
  );
}