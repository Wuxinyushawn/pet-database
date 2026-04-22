function toQuery(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function createVolunteersService(apiClient) {
  return {
    listVolunteers: (params) => apiClient.get(`/volunteers${toQuery(params)}`),
    listAssignments: (params) => apiClient.get(`/volunteers/assignments${toQuery(params)}`)
  };
}
