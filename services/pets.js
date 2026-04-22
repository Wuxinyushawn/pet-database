export function createPetsService(apiClient) {
  return {
    listPets: () => apiClient.get('/pets')
  };
}
