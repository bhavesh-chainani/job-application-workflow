import axios from 'axios';

const API_BASE_URL = '/api';

export interface Application {
  email_id: string;
  date: string | null;
  job_title: string | null;
  company: string | null;
  location: string | null;
  status: string;
  application_date: string | null;
  sender: string | null;
  subject: string | null;
  last_updated: string | null;
}

export interface Statistics {
  total: number;
  by_status: Record<string, number>;
  by_company: Record<string, number>;
  by_location: Record<string, number>;
}

export interface FunnelData {
  stage: string;
  count: number;
  percentage: number;
}

export const api = {
  getApplications: async (status?: string, company?: string): Promise<Application[]> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (company) params.append('company', company);
    
    const response = await axios.get<Application[]>(
      `${API_BASE_URL}/applications?${params.toString()}`
    );
    return response.data;
  },

  getStatistics: async (): Promise<Statistics> => {
    const response = await axios.get<Statistics>(`${API_BASE_URL}/statistics`);
    return response.data;
  },

  getFunnelData: async (): Promise<FunnelData[]> => {
    const response = await axios.get<FunnelData[]>(`${API_BASE_URL}/funnel`);
    return response.data;
  },

  updateStatus: async (emailId: string, status: string): Promise<void> => {
    await axios.put(`${API_BASE_URL}/applications/status`, {
      email_id: emailId,
      status,
    });
  },

  updateLocation: async (emailId: string, location: string | null): Promise<void> => {
    await axios.put(`${API_BASE_URL}/applications/location`, {
      email_id: emailId,
      location,
    });
  },
};











