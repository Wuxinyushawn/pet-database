export function createMedicalService(apiClient) {
  return {
    listMedicalRecords: () => apiClient.get('/medical/records'),
    createMedicalRecord: (payload) => apiClient.post('/medical/records', payload),
    updateMedicalRecord: (recordId, payload) => apiClient.patch(`/medical/records/${encodeURIComponent(recordId)}`, payload),
    deleteMedicalRecord: (recordId) => apiClient.delete(`/medical/records/${encodeURIComponent(recordId)}`),
    listVaccinations: () => apiClient.get('/medical/vaccinations'),
    createVaccination: (payload) => apiClient.post('/medical/vaccinations', payload),
    updateVaccination: (vaccinationId, payload) => apiClient.patch(`/medical/vaccinations/${encodeURIComponent(vaccinationId)}`, payload),
    deleteVaccination: (vaccinationId) => apiClient.delete(`/medical/vaccinations/${encodeURIComponent(vaccinationId)}`)
  };
}
