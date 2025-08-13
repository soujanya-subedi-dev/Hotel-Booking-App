import { useQuery } from '@tanstack/react-query';
import { listMyBookings, cancelBooking } from '../lib/bookings';
import toast from 'react-hot-toast';

export default function MyBookings(){
  const { data, isLoading, refetch } = useQuery({ queryKey:['my-bookings'], queryFn: listMyBookings });
  if (isLoading) return <p>Loading…</p>;
  const rows = data || [];

  const onCancel = async (id) => {
    try { await cancelBooking(id); toast.success('Cancelled'); refetch(); }
    catch (e) { toast.error(e?.normalized?.message || 'Cancel failed'); }
  };

  return (
    <div className="space-y-3">
      <h1 className="text-2xl font-bold">My Bookings</h1>

      {rows.length === 0 && <div className="text-sm text-gray-600">No bookings yet.</div>}

      {rows.map(b => (
        <div key={b.id} className="rounded-xl border p-3 bg-white shadow-sm">
          <div className="flex justify-between items-center">
            <div>
              <div className="font-semibold">{b.hotel_name} — {b.room_type_name}</div>
              <div className="text-sm text-gray-600">
                {String(b.check_in).slice(0,10)} → {String(b.check_out).slice(0,10)} · {b.status}
              </div>
            </div>
            {b.status !== 'cancelled' && (
              <button
                onClick={() => onCancel(b.id)}
                className="px-3 py-2 border rounded-md hover:bg-gray-50"
              >Cancel</button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
