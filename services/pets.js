export function createPetsService(apiClient) {
  return {
    listPets: () => apiClient.get('/pets'),
    createPet: (payload) => apiClient.post('/pets', payload),
    updatePet: (petId, payload) => apiClient.patch(`/pets/${encodeURIComponent(petId)}`, payload)
  };
}
