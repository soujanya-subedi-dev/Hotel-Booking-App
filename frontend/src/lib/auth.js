// Lightweight auth helpers around JWT in localStorage

const decode = (t) => {
  try { return JSON.parse(atob(t.split('.')[1] || '')) } catch { return null; }
};

export const getToken = () => localStorage.getItem('access_token') || null;

export const getUser = () => {
  const t = getToken();
  if (!t) return null;
  const p = decode(t);
  if (!p) return null;
  const now = Math.floor(Date.now()/1000);
  if (p.exp && p.exp < now) {
    // auto-expired -> cleanup
    localStorage.removeItem('access_token');
    return null;
  }
  return {
    id: p.sub ? parseInt(p.sub, 10) : null,
    email: p.email,
    role: p.role,
    exp: p.exp
  };
};

export const isLoggedIn = () => !!getUser();

export const logout = () => {
  localStorage.removeItem('access_token');
  window.location.assign('/');
};
