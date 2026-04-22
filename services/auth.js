export function createAuthService(apiClient) {
  return {
    login: (payload) => apiClient.post('/auth/login', payload),
    me: () => apiClient.get('/auth/me')
  };
}
