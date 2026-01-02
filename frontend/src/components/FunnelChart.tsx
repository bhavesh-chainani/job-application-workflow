import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { FunnelData } from '../api';

interface FunnelChartProps {
  data: FunnelData[];
}

const FunnelChart: React.FC<FunnelChartProps> = ({ data }) => {
  // Separate stages and outcomes
  const stages = data.filter(d => ['Applied', 'Recruiter Screen', 'Interview'].includes(d.stage));
  const outcomes = data.filter(d => !['Applied', 'Recruiter Screen', 'Interview'].includes(d.stage));

  // Color mapping
  const getColor = (stage: string): string => {
    const colors: Record<string, string> = {
      'Applied': '#F7DC6F',
      'Recruiter Screen': '#98D8C8',
      'Interview': '#4ECDC4',
      'Rejected': '#FF6B6B',
      'Ghosted': '#FFA07A',
      'Dropped': '#FFB6C1',
      'Offer': '#2ECC71',
    };
    return colors[stage] || '#94a3b8';
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{data.stage}</p>
          <p className="text-sm text-gray-600">
            Count: <span className="font-medium">{data.count}</span>
          </p>
          <p className="text-sm text-gray-600">
            Percentage: <span className="font-medium">{data.percentage}%</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-8">
      {/* Funnel Stages */}
      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Application Funnel</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={stages} layout="vertical">
            <XAxis type="number" />
            <YAxis dataKey="stage" type="category" width={120} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" radius={[0, 8, 8, 0]}>
              {stages.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.stage)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Outcomes */}
      {outcomes.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Outcomes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={outcomes} layout="vertical">
              <XAxis type="number" />
              <YAxis dataKey="stage" type="category" width={120} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[0, 8, 8, 0]}>
                {outcomes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getColor(entry.stage)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default FunnelChart;











