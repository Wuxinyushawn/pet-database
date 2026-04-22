export function createAuditService(apiClient) {
  return {
    listRecent: (limit = 20) => apiClient.get(`/audit-logs/recent?limit=${encodeURIComponent(limit)}`)
  };
}
