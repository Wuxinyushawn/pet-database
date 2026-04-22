export function createVolunteersService(apiClient) {
  return {
    listVolunteers: () => apiClient.get('/volunteers'),
    listAssignments: async () => {
      try {
        return await apiClient.get('/volunteers/assignments');
      } catch {
        return apiClient.get('/assignments');
      }
    },
    createAssignment: (payload) => apiClient.post('/volunteers/assignments', payload),
    updateAssignment: (assignmentId, payload) => apiClient.patch(`/volunteers/assignments/${encodeURIComponent(assignmentId)}`, payload)
  };
}
