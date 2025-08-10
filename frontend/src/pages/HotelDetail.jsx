import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export default function HotelDetail(){
  const { id } = useParams();
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['hotel', id, checkIn, checkOut],
    queryFn: async () => {
      const params = {};
      if (checkIn && checkOut) { params.check_in = checkIn; params.check_out = checkOut; }
      const res = await api.get(`/hotels/${id}`, { params });
      return res.data;
    }
  });

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p className="text-red-600">Failed to load hotel.</p>;
  if (!data?.hotel) return <p>Not found.</p>;

  const h = data.hotel;
  const availability = data.availability || {};

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{h.name}</h1>
      <p className="text-gray-600">{h.city}, {h.country}</p>
      <p className="text-sm">Status: <span className="font-medium">{h.occupancy.hotel_status}</span></p>

      {/* Images */}
      {h.images?.length > 0 && (
        <div className="flex gap-2 overflow-x-auto">
          {h.images.map(img => (
            <img key={img.id} src={img.url} alt={img.alt_text || h.name} className="h-40 rounded" />
          ))}
        </div>
      )}

      {/* Date pickers */}
      <div className="flex gap-2 items-end">
        <div>
          <label className="text-sm">Check-in</label>
          <input type="date" className="border p-2 block" value={checkIn} onChange={e=>setCheckIn(e.target.value)} />
        </div>
        <div>
          <label className="text-sm">Check-out</label>
          <input type="date" className="border p-2 block" value={checkOut} onChange={e=>setCheckOut(e.target.value)} />
        </div>
        <button onClick={()=>refetch()} className="h-10 px-4 bg-black text-white rounded">Check Availability</button>
      </div>

      {/* Room types */}
      <div className="grid md:grid-cols-2 gap-4">
        {data.room_types.map(rt => {
          const a = availability[String(rt.id)];
          return (
            <div key={rt.id} className="border rounded p-3 bg-white">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{rt.name}</h3>
                <span className="text-sm">${rt.base_price}</span>
              </div>
              <p className="text-sm text-gray-600">Capacity: {rt.capacity}</p>

              {checkIn && checkOut && (
                <p className="mt-1 text-sm">
                  {a?.any_available
                    ? <span className="text-green-700">{a.available_count} available</span>
                    : <span className="text-red-700">Unavailable</span>}
                </p>
              )}

              <button className="mt-3 px-3 py-2 bg-black text-white rounded">Book Now</button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

