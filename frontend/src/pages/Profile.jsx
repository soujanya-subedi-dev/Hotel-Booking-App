import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMe, updateMe, changePassword } from '../lib/me';
import toast from 'react-hot-toast';

export default function Profile(){
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({ queryKey:['me'], queryFn: getMe });

  const upd = useMutation({
    mutationFn: (b)=>updateMe(b),
    onSuccess: ()=>{ toast.success('Profile updated'); qc.invalidateQueries(['me']); }
  });

  const pwd = useMutation({
    mutationFn: ({cur, nxt})=>changePassword(cur, nxt),
    onSuccess: ()=>toast.success('Password changed')
  });

  if (isLoading) return <p>Loading…</p>;
  if (error) return <p className="text-red-600">Failed to load profile</p>;

  const onSave = (e)=>{
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    upd.mutate({ full_name: f.get('full_name'), phone: f.get('phone') });
  };

  const onPwd = (e)=>{
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const cur = f.get('current_password');
    const nxt = f.get('new_password');
    if (!nxt || nxt.length < 6) { toast.error('New password must be 6+ chars'); return; }
    pwd.mutate({ cur, nxt });
    e.currentTarget.reset();
  };

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <form onSubmit={onSave} className="bg-white p-4 border rounded-xl shadow-sm space-y-3">
        <h2 className="font-semibold">Profile</h2>
        <div>
          <label className="text-xs">Full name</label>
          <input name="full_name" defaultValue={data.full_name||''} className="border p-2 rounded-md w-full focus:ring-2 focus:ring-black/10"/>
        </div>
        <div>
          <label className="text-xs">Email</label>
          <input disabled defaultValue={data.email} className="border p-2 rounded-md w-full bg-gray-50"/>
        </div>
        <div>
          <label className="text-xs">Phone</label>
          <input name="phone" defaultValue={data.phone||''} className="border p-2 rounded-md w-full"/>
        </div>
        <button className="px-4 py-2 bg-black text-white rounded-md hover:bg-black/90">Save</button>
      </form>

      <form onSubmit={onPwd} className="bg-white p-4 border rounded-xl shadow-sm space-y-3">
        <h2 className="font-semibold">Change password</h2>
        <div>
          <label className="text-xs">Current password</label>
          <input type="password" name="current_password" className="border p-2 rounded-md w-full" required/>
        </div>
        <div>
          <label className="text-xs">New password</label>
          <input type="password" name="new_password" className="border p-2 rounded-md w-full" required/>
        </div>
        <button className="px-4 py-2 border rounded-md hover:bg-gray-50">Update Password</button>
      </form>
    </div>
  );
}
