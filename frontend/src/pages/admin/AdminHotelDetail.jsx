import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminGetHotel, adminUpdateHotel } from '../../lib/admin';

export default function AdminHotelDetail(){
  const { id } = useParams();
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({ queryKey:['admin-hotel', id], queryFn: ()=>adminGetHotel(id) });
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const mutation = useMutation({
    mutationFn: (updates) => adminUpdateHotel(id, updates),
    onSuccess: () => {
      qc.invalidateQueries(['admin-hotel', id]);
      setEditing(false);
    }
  });

  if (isLoading) return <p>Loading…</p>;
  if (error || !data) return <p className="text-red-600">Not found.</p>;
  const h = data;

  const images = h.images?.length ? h.images : [{ url: h.primary_image, alt_text: h.name }].filter(Boolean);

  const startEdit = () => {
    setForm({
      name: h.name,
      city: h.city,
      country: h.country,
      address: h.address || '',
      description: h.description || ''
    });
    setEditing(true);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Hotel — {h.name}</h1>

      {editing ? (
        <form className="bg-white p-4 rounded-xl border shadow-sm space-y-2" onSubmit={e=>{e.preventDefault(); mutation.mutate(form);}}>
          <input className="border p-2 w-full rounded" placeholder="Name" value={form.name} onChange={e=>setForm({...form, name:e.target.value})} />
          <div className="flex gap-2">
            <input className="border p-2 rounded w-1/2" placeholder="City" value={form.city} onChange={e=>setForm({...form, city:e.target.value})} />
            <input className="border p-2 rounded w-1/2" placeholder="Country" value={form.country} onChange={e=>setForm({...form, country:e.target.value})} />
          </div>
          <input className="border p-2 w-full rounded" placeholder="Address" value={form.address} onChange={e=>setForm({...form, address:e.target.value})} />
          <textarea className="border p-2 w-full rounded" placeholder="Description" value={form.description} onChange={e=>setForm({...form, description:e.target.value})} />
          <div className="flex gap-2">
            <button type="submit" className="px-3 py-2 bg-blue-600 text-white rounded" disabled={mutation.isLoading}>Save</button>
            <button type="button" className="px-3 py-2 border rounded" onClick={()=>setEditing(false)}>Cancel</button>
          </div>
          {mutation.error && <p className="text-red-600 text-sm">Update failed</p>}
        </form>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-xl border shadow-sm space-y-1">
            <div className="text-sm text-gray-600">{h.city}, {h.country}</div>
            <div className="text-sm">{h.address}</div>
            <div className="text-sm text-gray-600">Amenities: <code className="text-xs">{JSON.stringify(h.amenities || {})}</code></div>
            <p className="text-sm mt-2">{h.description}</p>
            <button className="mt-3 px-3 py-1 border rounded" onClick={startEdit}>Edit</button>
          </div>
          <div className="bg-white p-4 rounded-xl border shadow-sm">
            <div className="font-medium mb-2">Room Types</div>
            <div className="grid gap-2">
              {(h.room_types || []).map(rt => (
                <div key={rt.id} className="border rounded-md p-2 flex items-center justify-between">
                  <div>
                    <div className="font-medium">{rt.name}</div>
                    <div className="text-xs text-gray-600">Cap {rt.capacity}</div>
                  </div>
                  <div className="text-sm">${rt.base_price}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {images.length > 0 && (
        <div className="bg-white p-4 rounded-xl border shadow-sm">
          <div className="font-medium mb-2">Images</div>
          <div className="flex gap-2 overflow-x-auto">
            {images.map((img, i)=>(
              <img key={i} src={img.url} alt={img.alt_text||''} className="h-28 rounded-md"/>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
