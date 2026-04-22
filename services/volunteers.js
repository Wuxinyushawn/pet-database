export function createVolunteersService(apiClient) {
  return {
    listVolunteers: () => apiClient.get('/volunteers'),
    listAssignments: () => apiClient.get('/volunteers/assignments'),
    createAssignment: (payload) => apiClient.post('/volunteers/assignments', payload),
    updateAssignment: (assignmentId, payload) => apiClient.patch(`/volunteers/assignments/${encodeURIComponent(assignmentId)}`, payload)
  };
}
