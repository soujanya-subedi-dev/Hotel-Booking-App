import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import toast from 'react-hot-toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/auth/login', { email, password });
      localStorage.setItem('access_token', data.access_token);
      toast.success('Welcome back');
      nav('/');
    } catch (err) {
      toast.error(err?.normalized?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="max-w-sm space-y-4 p-6 bg-white rounded-xl border shadow-sm mx-auto">
      <h1 className="text-xl font-semibold">Login</h1>
      <input
        className="border p-2 w-full rounded-md focus:ring-2 focus:ring-black/10"
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />
      <input
        className="border p-2 w-full rounded-md focus:ring-2 focus:ring-black/10"
        placeholder="Password"
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />
      <button disabled={loading} className="bg-black text-white px-3 py-2 rounded-md w-full hover:bg-black/90 disabled:opacity-50">
        {loading ? 'Signing in…' : 'Login'}
      </button>
      <div className="text-sm text-gray-600 text-center">
        No account? <Link className="underline" to="/register">Register</Link>
      </div>
    </form>
  );
}
