import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminListHotels, adminCreateHotel } from '../../lib/admin';

export default function AdminHotels(){
  const qc = useQueryClient();
  const [search, setSearch] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-hotels', search],
    queryFn: () => adminListHotels({ search, page: 1, limit: 20 })
  });

  const createMut = useMutation({
    mutationFn: adminCreateHotel,
    onSuccess: () => { toast.success('Hotel created'); qc.invalidateQueries(['admin-hotels']); }
  });

  const submitCreate = (e)=>{
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    createMut.mutate({
      name: f.get('name'), city: f.get('city'), country: f.get('country'),
      star_rating: Number(f.get('star_rating') || 0)
    });
    e.currentTarget.reset();
  };

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Hotels</h1>

      <div className="flex gap-2">
        <input className="border p-2 rounded" placeholder="Search name/city"
               value={search} onChange={e=>setSearch(e.target.value)} />
      </div>

      <form onSubmit={submitCreate} className="flex flex-wrap gap-2 items-end border p-3 rounded">
        <div><label className="text-xs">Name</label><input name="name" className="border p-2 rounded block" required/></div>
        <div><label className="text-xs">City</label><input name="city" className="border p-2 rounded block" required/></div>
        <div><label className="text-xs">Country</label><input name="country" className="border p-2 rounded block" required/></div>
        <div><label className="text-xs">Stars</label><input name="star_rating" type="number" min={0} max={5} className="border p-2 rounded block w-20"/></div>
        <button className="px-3 py-2 bg-black text-white rounded">Add</button>
      </form>

      {isLoading && <p>Loading…</p>}
      {error && <p className="text-red-600">Failed to load</p>}

      <div className="grid md:grid-cols-2 gap-3">
        {(data?.items || []).map(h => (
          <div key={h.id} className="border rounded p-3 bg-white">
            <div className="flex justify-between">
              <div>
                <div className="font-semibold">{h.name}</div>
                <div className="text-sm text-gray-600">{h.city}, {h.country}</div>
              </div>
              <Link to={`/admin/hotels/${h.id}`} className="px-3 py-2 border rounded">Manage</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
