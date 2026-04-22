export function createMedicalService(apiClient) {
  return {
    listMedicalRecords: () => apiClient.get('/medical/records'),
    listVaccinations: () => apiClient.get('/medical/vaccinations')
  };
}
