import { api } from './api';

// Lists
export const adminListHotels = (params) => api.get('/admin/hotels', { params }).then(r => r.data);
export const adminGetHotel   = (id)     => api.get(`/admin/hotels/${id}`).then(r => r.data);
export const adminListRT     = (params) => api.get('/admin/room-types', { params }).then(r => r.data);
export const adminListRooms  = (params) => api.get('/admin/rooms', { params }).then(r => r.data);

// CRUD
export const adminCreateHotel = (b)    => api.post('/admin/hotels', b).then(r => r.data);
export const adminUpdateHotel = (id,b) => api.patch(`/admin/hotels/${id}`, b).then(r => r.data);
export const adminDeleteHotel = (id)   => api.delete(`/admin/hotels/${id}`).then(r => r.data);

export const adminCreateRT    = (b)    => api.post('/admin/room-types', b).then(r => r.data);
export const adminUpdateRT    = (id,b) => api.patch(`/admin/room-types/${id}`, b).then(r => r.data);
export const adminDeleteRT    = (id)   => api.delete(`/admin/room-types/${id}`).then(r => r.data);

export const adminCreateRoom  = (b)    => api.post('/admin/rooms', b).then(r => r.data);
export const adminUpdateRoom  = (id,b) => api.patch(`/admin/rooms/${id}`, b).then(r => r.data);
export const adminDeleteRoom  = (id)   => api.delete(`/admin/rooms/${id}`).then(r => r.data);

// Images
export const adminAddImage    = (hid,b)=> api.post(`/admin/hotels/${hid}/images`, b).then(r => r.data);
export const adminUpdateImage = (id,b) => api.patch(`/admin/hotel-images/${id}`, b).then(r => r.data);
export const adminDeleteImage = (id)   => api.delete(`/admin/hotel-images/${id}`).then(r => r.data);

// Reports
export const adminReportOcc   = (hid)  => api.get(`/admin/reports/hotel/${hid}/occupancy`).then(r => r.data);
export const adminReportUsers = (hid)  => api.get(`/admin/reports/hotel/${hid}/user-bookings`).then(r => r.data);
export const adminReportUser  = (uid)  => api.get(`/admin/reports/user/${uid}/bookings`).then(r => r.data);
