import { useQuery } from '@tanstack/react-query';
import { listMyBookings, cancelBooking } from '../lib/bookings';

export default function MyBookings(){
  const { data, isLoading, refetch } = useQuery({ queryKey:['my-bookings'], queryFn: listMyBookings });
  if (isLoading) return <p>Loading…</p>;
  return (
    <div className="space-y-3">
      <h1 className="text-2xl font-bold">My Bookings</h1>
      {(data||[]).map(b => (
        <div key={b.id} className="border rounded p-3 bg-white">
          <div className="flex justify-between">
            <div>
              <div className="font-semibold">{b.hotel.name} — {b.room_type.name}</div>
              <div className="text-sm text-gray-600">{b.check_in.slice(0,10)} → {b.check_out.slice(0,10)} · {b.status}</div>
            </div>
            {b.status !== 'cancelled' && (
              <button
                onClick={async () => { await cancelBooking(b.id); refetch(); }}
                className="px-3 py-2 border rounded"
              >Cancel</button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
