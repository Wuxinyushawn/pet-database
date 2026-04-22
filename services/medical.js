function toQuery(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function createMedicalService(apiClient) {
  return {
    listMedicalRecords: (params) => apiClient.get(`/medical/records${toQuery(params)}`),
    listVaccinations: (params) => apiClient.get(`/medical/vaccinations${toQuery(params)}`)
  };
}
