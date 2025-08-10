export const getToken = () => localStorage.getItem('access_token');

export const getUser = () => {
  const t = getToken();
  if (!t) return null;
  try {
    const payload = JSON.parse(atob(t.split('.')[1]));
    return {
      id: payload.sub ? parseInt(payload.sub, 10) : null,
      email: payload.email,
      role: payload.role,
      exp: payload.exp,
    };
  } catch {
    return null;
  }
};

export const isLoggedIn = () => !!getToken();

export const logout = () => {
  localStorage.removeItem('access_token');
  window.location.href = '/';
};
