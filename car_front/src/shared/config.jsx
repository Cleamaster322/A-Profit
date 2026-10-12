const backendHost = window.location.hostname || '127.0.0.1'

export const baseURL = import.meta.env.VITE_API_URL || `http://${backendHost}:8000`