import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { adminGetHotel } from '../../lib/admin';

export default function AdminHotelDetail(){
  const { id } = useParams();

  const { data, isLoading, error } = useQuery({ queryKey:['admin-hotel', id], queryFn: ()=>adminGetHotel(id) });

  if (isLoading) return <p>Loading…</p>;
  if (error || !data) return <p className="text-red-600">Not found.</p>;
  const h = data;

  const images = h.images?.length ? h.images : [{ url: h.primary_image, alt_text: h.name }].filter(Boolean);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Hotel — {h.name}</h1>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-xl border shadow-sm space-y-1">
          <div className="text-sm text-gray-600">{h.city}, {h.country}</div>
          <div className="text-sm">{h.address}</div>
          <div className="text-sm text-gray-600">Amenities: <code className="text-xs">{JSON.stringify(h.amenities || {})}</code></div>
          <p className="text-sm mt-2">{h.description}</p>
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

      <div className="text-xs text-gray-500">
        Note: Admin CRUD is disabled in backend v1. This page is read-only for now.
      </div>
    </div>
  );
}
