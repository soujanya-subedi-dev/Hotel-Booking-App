import { useState } from 'react'

export default function Register(){
  const [full_name, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState('')

  const submit = async (e)=>{
    e.preventDefault()
    setMsg('')
    try{
      const res = await fetch(import.meta.env.VITE_API_BASE_URL + '/auth/register',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({full_name, email, password})
      })
      const data = await res.json()
      if(!res.ok) throw new Error(data.error || 'Registration failed')
      setMsg('Registered. You can login now.')
    }catch(err){ setMsg(err.message) }
  }

  return (
    <form onSubmit={submit} className="max-w-sm space-y-3">
      <h1 className="text-xl font-semibold">Register</h1>
      <input className="border p-2 w-full" placeholder="Full name" value={full_name} onChange={e=>setFullName(e.target.value)} />
      <input className="border p-2 w-full" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
      <input className="border p-2 w-full" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button className="bg-black text-white px-3 py-2 rounded">Create account</button>
      {msg && <p className="text-sm text-gray-600">{msg}</p>}
    </form>
  )
}
