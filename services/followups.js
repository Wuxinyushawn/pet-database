export function createFollowupsService(apiClient) {
  return {
    listFollowups: () => apiClient.get('/followups'),
    createFollowup: (payload) => apiClient.post('/followups', payload),
    updateFollowup: (followupId, payload) => apiClient.patch(`/followups/${encodeURIComponent(followupId)}`, payload)
  };
}
