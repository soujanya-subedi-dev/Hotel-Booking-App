import { api } from './api';

export const getMe = () => api.get('/me').then(r => r.data);
export const updateMe = (b) => api.patch('/me', b).then(r => r.data);
export const changePassword = (current_password, new_password) =>
  api.patch('/me/password', { current_password, new_password }).then(r => r.data);

export const myHotelCount = (hotelId) =>
  api.get(`/me/reports/hotel/${hotelId}/count`).then(r => r.data);
