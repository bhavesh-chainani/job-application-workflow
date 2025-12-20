import React, { useState, useEffect } from 'react';
import { Application, Statistics, FunnelData, api } from './api';
import Metrics from './components/Metrics';
import FunnelChart from './components/FunnelChart';
import ApplicationTable from './components/ApplicationTable';
import { RefreshCw, Filter } from 'lucide-react';

function App() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [funnelData, setFunnelData] = useState<FunnelData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [companyFilter, setCompanyFilter] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [apps, stats, funnel] = await Promise.all([
        api.getApplications(statusFilter || undefined, companyFilter || undefined),
        api.getStatistics(),
        api.getFunnelData(),
      ]);
      setApplications(apps);
      setStatistics(stats);
      setFunnelData(funnel);
    } catch (err) {
      setError('Failed to load data. Make sure the backend server is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, companyFilter]);

  const handleRefresh = () => {
    loadData();
  };

  const uniqueStatuses = Array.from(new Set(applications.map(a => a.status))).sort();
  const uniqueCompanies = Array.from(new Set(applications.map(a => a.company).filter(Boolean))).sort();

  if (loading && !statistics) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Job Application Workflow
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Bhavesh Chainani - Application Pipeline Management
              </p>
            </div>
            <button
              onClick={handleRefresh}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Filters */}
        <div className="mb-6 bg-white rounded-lg shadow-md p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold text-gray-700">Filters</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Statuses</option>
                {uniqueStatuses.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company
              </label>
              <select
                value={companyFilter}
                onChange={(e) => setCompanyFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Companies</option>
                {uniqueCompanies.map((company) => (
                  <option key={company} value={company}>
                    {company}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Metrics */}
        {statistics && <Metrics statistics={statistics} />}

        {/* Funnel Chart */}
        {funnelData.length > 0 && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <FunnelChart data={funnelData} />
          </div>
        )}

        {/* Application Table */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Applications</h2>
          <ApplicationTable applications={applications} onUpdate={loadData} />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-600">
            Bhavesh Chainani - Job Application Management System
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

