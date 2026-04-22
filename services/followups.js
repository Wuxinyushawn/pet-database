export function createFollowupsService(apiClient) {
  return {
    listFollowups: () => apiClient.get('/followups'),
    createFollowup: (payload) => apiClient.post('/followups', payload)
  };
}
