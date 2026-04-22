export function createVolunteersService(apiClient) {
  return {
    listVolunteers: () => apiClient.get('/volunteers'),
    listAssignments: async () => {
      try {
        return await apiClient.get('/assignments');
      } catch {
        return apiClient.get('/volunteers/assignments');
      }
    }
  };
}
