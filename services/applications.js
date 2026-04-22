function toQuery(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function createApplicationsService(apiClient) {
  return {
    listApplications: (params) => apiClient.get(`/applications${toQuery(params)}`),
    exportApplicationsCsv: (params) => window.open(`/api/applications/export${toQuery(params)}`, '_blank'),
    createApplication: (payload) => apiClient.post('/applications', payload),
    reviewApplication: (applicationId, payload) => apiClient.patch(`/applications/${encodeURIComponent(applicationId)}/review`, payload)
  };
}
