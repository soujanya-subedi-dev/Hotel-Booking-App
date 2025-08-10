import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

export default function Home(){
  const [q, setQ] = useState('');
  const [city, setCity] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['hotels', q, city],
    queryFn: async () => {
      const res = await api.get('/hotels', { params: { q, city } });
      return res.data;
    }
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Browse Hotels & Rooms</h1>

      {/* Search */}
      <div className="flex gap-2">
        <input className="border p-2 w-64" placeholder="Search hotel or city"
               value={q} onChange={e=>setQ(e.target.value)} />
        <input className="border p-2 w-48" placeholder="City"
               value={city} onChange={e=>setCity(e.target.value)} />
        <button onClick={()=>refetch()} className="bg-black text-white px-4 py-2 rounded">Search</button>
      </div>

      {isLoading && <p>Loading...</p>}
      {error && <p className="text-red-600">Failed to load hotels</p>}

      {/* Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(data || []).map(h => (
          <div key={h.id} className="border bg-white rounded p-3 flex flex-col">
            {h.primary_image ? (
              <img src={h.primary_image} alt={h.name} className="h-40 w-full object-cover rounded" />
            ) : <div className="h-40 w-full bg-gray-100 rounded" />}

            <div className="mt-3">
              <h3 className="font-semibold text-lg">{h.name}</h3>
              <p className="text-sm text-gray-600">{h.city}, {h.country}</p>
              <p className="text-sm mt-1">
                Status: <span className="font-medium">{h.occupancy.hotel_status}</span>
              </p>

              {/* sample room types */}
              {h.sample_room_types?.length > 0 && (
                <div className="mt-2 text-sm">
                  {h.sample_room_types.map(rt => (
                    <div key={rt.id} className="flex justify-between">
                      <span>{rt.name} · {rt.capacity} pax</span>
                      <span>${rt.base_price}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-3 flex gap-2">
                <Link to={`/hotels/${h.id}`} className="px-3 py-2 border rounded">Details</Link>
                <Link to={`/hotels/${h.id}`} className="px-3 py-2 bg-black text-white rounded">Book Now</Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
