// Admin data-access aligned to backend v1.
// We keep the old function names as no-op/stubs (throw) when not supported
// to avoid compile-time crashes in pages awaiting refactor.

import { api } from './api';

// Supported in backend v1
export const adminListUsers    = () => api.get('/admin/users').then(r => r.data);
export const adminListBookings = () => api.get('/admin/bookings').then(r => r.data);

// ---- Legacy hotel management (NOT supported in backend v1) ----
const notSupported = (name) => () => Promise.reject(new Error(`${name} not supported in backend v1`));

export const adminListHotels = (params) => api.get('/hotels', { params }).then(r => r.data); // read-only via public route
export const adminGetHotel   = (id)     => api.get(`/hotels/${id}`).then(r => r.data);

export const adminListRT     = notSupported('adminListRT');
export const adminListRooms  = notSupported('adminListRooms');

export const adminCreateHotel = notSupported('adminCreateHotel');
export const adminUpdateHotel = (id, data) => api.patch(`/admin/hotels/${id}`, data).then(r => r.data);
export const adminDeleteHotel = notSupported('adminDeleteHotel');

export const adminCreateRT    = notSupported('adminCreateRT');
export const adminUpdateRT    = notSupported('adminUpdateRT');
export const adminDeleteRT    = notSupported('adminDeleteRT');

export const adminCreateRoom  = notSupported('adminCreateRoom');
export const adminUpdateRoom  = notSupported('adminUpdateRoom');
export const adminDeleteRoom  = notSupported('adminDeleteRoom');

// Images
export const adminAddImage    = notSupported('adminAddImage');
export const adminUpdateImage = notSupported('adminUpdateImage');
export const adminDeleteImage = notSupported('adminDeleteImage');

// Reports (future; compute client-side for now)
export const adminReportOcc   = notSupported('adminReportOcc');
export const adminReportUsers = notSupported('adminReportUsers');
export const adminReportUser  = notSupported('adminReportUser');
