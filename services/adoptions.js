export function createAdoptionsService(apiClient) {
  return {
    listAdoptions: () => apiClient.get('/adoptions'),
    createAdoption: (payload) => apiClient.post('/adoptions', payload)
  };
}
