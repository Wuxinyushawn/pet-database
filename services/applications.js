export function createApplicationsService(apiClient) {
  return {
    listApplications: () => apiClient.get('/applications'),
    createApplication: (payload) => apiClient.post('/applications', payload),
    reviewApplication: (applicationId, payload) => apiClient.patch(`/applications/${encodeURIComponent(applicationId)}/review`, payload)
  };
}
