import { useState } from 'react'

export default function Login(){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState('')

  const submit = async (e)=>{
    e.preventDefault()
    setMsg('')
    try{
      const res = await fetch(import.meta.env.VITE_API_BASE_URL + '/auth/login',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({email, password})
      })
      const data = await res.json()
      if(!res.ok) throw new Error(data.error || 'Login failed')
      localStorage.setItem('access_token', data.access_token)
      setMsg('Logged in!')
    }catch(err){ setMsg(err.message) }
  }

  return (
    <form onSubmit={submit} className="max-w-sm space-y-3">
      <h1 className="text-xl font-semibold">Login</h1>
      <input className="border p-2 w-full" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
      <input className="border p-2 w-full" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button className="bg-black text-white px-3 py-2 rounded">Login</button>
      {msg && <p className="text-sm text-gray-600">{msg}</p>}
    </form>
  )
}
