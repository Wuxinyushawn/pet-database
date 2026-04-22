function toQuery(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function createAdoptionsService(apiClient) {
  return {
    listAdoptions: (params) => apiClient.get(`/adoptions${toQuery(params)}`),
    createAdoption: (payload) => apiClient.post('/adoptions', payload)
  };
}
