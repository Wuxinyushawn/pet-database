export function createVolunteersService(apiClient) {
  return {
    listVolunteers: () => apiClient.get('/volunteers'),
    listAssignments: () => apiClient.get('/volunteers/assignments')
  };
}
