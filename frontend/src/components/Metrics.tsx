import React from 'react';
import { Statistics } from '../api';
import { Briefcase, MapPin, FileText, TrendingUp } from 'lucide-react';

interface MetricsProps {
  statistics: Statistics;
}

const Metrics: React.FC<MetricsProps> = ({ statistics }) => {
  const metrics = [
    {
      label: 'Total Applications',
      value: statistics.total,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      label: 'Unique Companies',
      value: Object.keys(statistics.by_company || {}).length,
      icon: Briefcase,
      color: 'bg-green-500',
    },
    {
      label: 'Unique Locations',
      value: Object.keys(statistics.by_location || {}).length,
      icon: MapPin,
      color: 'bg-purple-500',
    },
    {
      label: 'In Progress',
      value: (statistics.by_status?.['Recruiter Screen'] || 0) + 
             (statistics.by_status?.['Interview'] || 0),
      icon: TrendingUp,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        return (
          <div
            key={index}
            className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">
                  {metric.label}
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {metric.value}
                </p>
              </div>
              <div className={`${metric.color} p-3 rounded-full`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Metrics;

