// frontend/src/lib/bookings.js
import { api } from './api';
export const createBooking   = (payload)         => api.post('/bookings', payload).then(r => r.data);
export const listMyBookings  = (params = {})     => api.get('/bookings', { params }).then(r => r.data);
export const getBooking      = (id)              => api.get(`/bookings/${id}`).then(r => r.data);
export const updateBooking   = (id, body)        => api.patch(`/bookings/${id}`, body).then(r => r.data);
export const cancelBooking   = (id)              => api.delete(`/bookings/${id}`).then(r => r.data);
