import React, { useState } from 'react';
import { Application, api } from '../api';
import { config } from '../config';

interface ApplicationTableProps {
  applications: Application[];
  onUpdate: () => void;
}

const ApplicationTable: React.FC<ApplicationTableProps> = ({ applications, onUpdate }) => {
  const [editing, setEditing] = useState<Record<string, { status?: string; location?: string }>>({});
  const [saving, setSaving] = useState(false);

  const handleStatusChange = (emailId: string, newStatus: string) => {
    setEditing(prev => ({
      ...prev,
      [emailId]: { ...prev[emailId], status: newStatus },
    }));
  };

  const handleLocationChange = (emailId: string, newLocation: string) => {
    setEditing(prev => ({
      ...prev,
      [emailId]: { ...prev[emailId], location: newLocation },
    }));
  };

  const saveChanges = async (emailId: string) => {
    setSaving(true);
    try {
      const changes = editing[emailId];
      if (changes?.status) {
        await api.updateStatus(emailId, changes.status);
      }
      if (changes?.location !== undefined) {
        await api.updateLocation(emailId, changes.location || null);
      }
      setEditing(prev => {
        const newEditing = { ...prev };
        delete newEditing[emailId];
        return newEditing;
      });
      onUpdate();
    } catch (error) {
      console.error('Failed to save changes:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  if (applications.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-500">No applications found.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Job Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {applications.map((app) => {
              const isEditing = editing[app.email_id];
              const currentStatus = isEditing?.status ?? app.status;
              const currentLocation = isEditing?.location ?? app.location ?? '';

              return (
                <tr key={app.email_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(app.date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {app.company || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {app.job_title || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <input
                      type="text"
                      value={currentLocation}
                      onChange={(e) => handleLocationChange(app.email_id, e.target.value)}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="Enter location..."
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <select
                      value={currentStatus}
                      onChange={(e) => handleStatusChange(app.email_id, e.target.value)}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    >
                      {config.STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {(isEditing?.status !== undefined || isEditing?.location !== undefined) && (
                      <button
                        onClick={() => saveChanges(app.email_id)}
                        disabled={saving}
                        className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 text-sm"
                      >
                        {saving ? 'Saving...' : 'Save'}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ApplicationTable;











