import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { adminListHotels } from '../../lib/admin';

export default function AdminHotels(){
  const [search, setSearch] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-hotels', search],
    queryFn: () => adminListHotels({ q: search })
  });

  const hotels = data || [];

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Hotels</h1>

      <div className="flex gap-2">
        <input className="border p-2 rounded-md" placeholder="Search name/city"
               value={search} onChange={e=>setSearch(e.target.value)} />
      </div>

      {isLoading && <p>Loading…</p>}
      {error && <p className="text-red-600">Failed to load</p>}

      <div className="grid md:grid-cols-2 gap-3">
        {hotels.map(h => (
          <div key={h.id} className="border rounded-xl p-3 bg-white shadow-sm">
            <div className="flex justify-between items-center">
              <div>
                <div className="font-semibold">{h.name}</div>
                <div className="text-sm text-gray-600">{h.city}, {h.country}</div>
              </div>
              <Link to={`/admin/hotels/${h.id}`} className="px-3 py-2 border rounded-md hover:bg-gray-50">View</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
