import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

function CardSkeleton() {
  return <div className="rounded-xl overflow-hidden border bg-white shadow-sm">
    <div className="h-40 bg-gray-100 animate-pulse" />
    <div className="p-3 space-y-2">
      <div className="h-4 bg-gray-100 rounded w-2/3 animate-pulse" />
      <div className="h-3 bg-gray-100 rounded w-1/2 animate-pulse" />
      <div className="h-8 bg-gray-100 rounded animate-pulse" />
    </div>
  </div>;
}

export default function Home() {
  const [q, setQ] = useState('');
  const [city, setCity] = useState('');

  const { data, isLoading, isFetching, error, refetch } = useQuery({
    queryKey: ['hotels', q, city],
    queryFn: async () => (await api.get('/hotels', { params: { q, city } })).data
  });

  const hotels = data || [];

  return (
    <div className="space-y-6">
      <div className="bg-white p-4 rounded-xl border shadow-sm">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-end">
          <div>
            <label className="text-xs text-gray-600">Search</label>
            <input
              className="border p-2 w-72 block rounded-md focus:ring-2 focus:ring-black/10"
              placeholder="Hotel or city"
              value={q}
              onChange={e => setQ(e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">City</label>
            <input
              className="border p-2 w-56 block rounded-md focus:ring-2 focus:ring-black/10"
              value={city}
              onChange={e => setCity(e.target.value)}
            />
          </div>
          <button
            onClick={() => refetch()}
            className="h-10 px-4 rounded-md bg-black text-white hover:bg-black/90 active:scale-[0.99] disabled:opacity-50"
            disabled={isFetching}
          >
            {isFetching ? 'Searching…' : 'Search'}
          </button>
        </div>
      </div>

      {error && <p className="text-red-600">Failed to load hotels</p>}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)
          : hotels.map(h => {
              const imgSrc = h.primary_image || `https://source.unsplash.com/random/400x300/?hotel&sig=${h.id}`;
              return (
                <div key={h.id} className="rounded-xl overflow-hidden border bg-white shadow-sm hover:shadow-lg transition-all hover:-translate-y-0.5">
                  <img src={imgSrc} alt={h.name} className="h-40 w-full object-cover" />
                  <div className="p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{h.name}</h3>
                      <span className="text-xs px-2 py-0.5 rounded-full border bg-gray-50">{h.city}</span>
                    </div>
                    <p className="text-sm text-gray-600">{h.city}, {h.country}</p>
                    <div className="mt-3 flex gap-2">
                      <Link to={`/hotels/${h.id}`} className="px-3 py-2 border rounded-md hover:bg-gray-50">Details</Link>
                      <Link to={`/hotels/${h.id}`} className="px-3 py-2 rounded-md bg-black text-white hover:bg-black/90">Book Now</Link>
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
