export function createMedicalService(apiClient) {
  return {
    listMedicalRecords: async () => {
      try {
        return await apiClient.get('/medical-records');
      } catch {
        return apiClient.get('/medical/records');
      }
    },
    listVaccinations: async () => {
      try {
        return await apiClient.get('/vaccinations');
      } catch {
        return apiClient.get('/medical/vaccinations');
      }
    }
  };
}
