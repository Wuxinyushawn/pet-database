function toQuery(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function createPetsService(apiClient) {
  return {
    listPets: (params) => apiClient.get(`/pets${toQuery(params)}`),
    exportPetsCsv: (params) => window.open(`/api/pets/export${toQuery(params)}`, '_blank')
  };
}
