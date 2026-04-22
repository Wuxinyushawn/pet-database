function toQuery(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function createFollowupsService(apiClient) {
  return {
    listFollowups: (params) => apiClient.get(`/followups${toQuery(params)}`),
    createFollowup: (payload) => apiClient.post('/followups', payload)
  };
}
