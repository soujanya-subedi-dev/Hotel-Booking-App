import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

function CardSkeleton() {
  return <div className="h-64 rounded bg-gray-100 animate-pulse" />;
}

export default function Home() {
  const [q, setQ] = useState('');
  const [city, setCity] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['hotels', q, city],
    queryFn: async () => (await api.get('/hotels', { params: { q, city } })).data
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-2 sm:items-end bg-white p-4 rounded shadow">
        <div>
          <label className="text-sm">Search</label>
          <input className="border p-2 w-72 block rounded" placeholder="Hotel or city" value={q} onChange={e => setQ(e.target.value)} />
        </div>
        <div>
          <label className="text-sm">City</label>
          <input className="border p-2 w-56 block rounded" value={city} onChange={e => setCity(e.target.value)} />
        </div>
        <button onClick={() => refetch()} className="h-10 px-4 bg-black text-white rounded">Search</button>
      </div>

      {error && <p className="text-red-600">Failed to load hotels</p>}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)
          : (data || []).map(h => {
              const imgSrc = h.primary_image || `https://source.unsplash.com/random/400x300/?hotel&sig=${h.id}`;
              return (
                <div key={h.id} className="border bg-white rounded overflow-hidden shadow-sm hover:shadow-lg transition-transform hover:-translate-y-1">
                  <img src={imgSrc} alt={h.name} className="h-40 w-full object-cover" />
                  <div className="p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{h.name}</h3>
                      <span className="text-xs px-2 py-0.5 rounded-full border">{h.occupancy.hotel_status}</span>
                    </div>
                    <p className="text-sm text-gray-600">{h.city}, {h.country}</p>
                    {h.sample_room_types?.length > 0 && (
                      <div className="mt-2 text-sm space-y-1">
                        {h.sample_room_types.map(rt => (
                          <div key={rt.id} className="flex justify-between text-gray-700">
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
              );
            })
        }
      </div>
    </div>
  );
}
