import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import BookingModal from '../components/BookingModal';
import toast from 'react-hot-toast';

export default function HotelDetail(){
  const { id } = useParams();
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [open, setOpen] = useState(false);
  const [selectedRt, setSelectedRt] = useState(null);

  // 1) Base hotel detail
  const hotelQ = useQuery({
    queryKey: ['hotel', id],
    queryFn: async () => (await api.get(`/hotels/${id}`)).data
  });

  // 2) Availability (only when dates selected)
  const availQ = useQuery({
    queryKey: ['availability', id, checkIn, checkOut],
    enabled: Boolean(checkIn && checkOut),
    queryFn: async () => (await api.get(`/hotels/${id}/availability`, { params: { check_in: checkIn, check_out: checkOut, guests: 1 } })).data
  });

  if (hotelQ.isLoading) return <p>Loading…</p>;
  if (hotelQ.error || !hotelQ.data) return <p className="text-red-600">Failed to load hotel.</p>;

  const h = hotelQ.data;
  const images = h.images?.length ? h.images : [{ url: h.primary_image || `https://source.unsplash.com/random/800x600/?hotel&sig=${h.id}`, alt_text: h.name }];

  const openModal = (rt) => {
    if (!checkIn || !checkOut) { toast.error('Pick dates first'); return; }
    setSelectedRt(rt);
    setOpen(true);
  };

  const availableIds = new Set((availQ.data || []).map(x => x.id));

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">{h.name}</h1>
          <p className="text-gray-600">{h.city}, {h.country}</p>
        </div>
        <div className="flex gap-2 items-end">
          <div>
            <label className="text-xs">Check-in</label>
            <input type="date" className="border p-2 block rounded-md" value={checkIn} onChange={e=>setCheckIn(e.target.value)} />
          </div>
          <div>
            <label className="text-xs">Check-out</label>
            <input type="date" className="border p-2 block rounded-md" value={checkOut} onChange={e=>setCheckOut(e.target.value)} />
          </div>
          <button onClick={()=>availQ.refetch()} className="h-10 px-4 rounded-md bg-black text-white hover:bg-black/90">Check Availability</button>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto rounded">
        {images.map((img, i) => (
          <img key={i} src={img.url} alt={img.alt_text || h.name} className="h-40 rounded-md" />
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {(h.room_types || []).map(rt => {
          const isAvailable = !checkIn || !checkOut ? true : availableIds.has(rt.id);
          return (
            <div key={rt.id} className="border rounded-xl p-3 bg-white hover:shadow transition">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{rt.name}</h3>
                <span className="text-sm">${rt.base_price}</span>
              </div>
              <p className="text-sm text-gray-600">Capacity: {rt.capacity}</p>
              {checkIn && checkOut && (
                <p className={"mt-1 text-sm " + (isAvailable ? "text-green-700" : "text-red-700")}>
                  {isAvailable ? 'Available' : 'Unavailable'}
                </p>
              )}
              <button onClick={()=>openModal(rt)} className="mt-3 px-3 py-2 rounded-md bg-black text-white hover:bg-black/90">Book Now</button>
            </div>
          );
        })}
      </div>

      {selectedRt && (
        <BookingModal
          open={open}
          onClose={()=>setOpen(false)}
          hotel={h}
          roomType={selectedRt}
          checkIn={checkIn}
          checkOut={checkOut}
        />
      )}
    </div>
  );
}
