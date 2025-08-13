// Booking client bound to backend v1 routes
import { api } from './api';

export const createBooking  = (payload)     => api.post('/bookings', payload).then(r => r.data);
export const listMyBookings = (params = {}) => api.get('/bookings', { params }).then(r => r.data);

// NOTE: backend v1 does not expose GET /bookings/:id or PATCH /bookings/:id updates
export const getBooking     = (_id)         => Promise.reject(new Error('getBooking not supported in backend v1'));
export const updateBooking  = (_id, _body)  => Promise.reject(new Error('updateBooking not supported in backend v1'));

// Correct cancel endpoint: PATCH /bookings/:id/cancel
export const cancelBooking  = (id)          => api.patch(`/bookings/${id}/cancel`).then(r => r.data);
