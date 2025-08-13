import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import toast from 'react-hot-toast';

export default function Register(){
  const [full_name, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  const submit = async (e)=>{
    e.preventDefault();
    setLoading(true);
    try{
      await api.post('/auth/register', { full_name, email, password });
      toast.success('Registered! You can login now.');
      nav('/login');
    }catch(err){
      toast.error(err?.normalized?.message || 'Registration failed');
    }finally{
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="max-w-sm space-y-4 p-6 bg-white rounded-xl border shadow-sm mx-auto">
      <h1 className="text-xl font-semibold">Create your account</h1>
      <input className="border p-2 w-full rounded-md focus:ring-2 focus:ring-black/10" placeholder="Full name" value={full_name} onChange={e=>setFullName(e.target.value)} />
      <input className="border p-2 w-full rounded-md focus:ring-2 focus:ring-black/10" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
      <input className="border p-2 w-full rounded-md focus:ring-2 focus:ring-black/10" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button disabled={loading} className="bg-black text-white px-3 py-2 rounded-md w-full hover:bg-black/90 disabled:opacity-50">Create account</button>
      <div className="text-sm text-gray-600 text-center">
        Already have an account? <Link className="underline" to="/login">Login</Link>
      </div>
    </form>
  )
}
