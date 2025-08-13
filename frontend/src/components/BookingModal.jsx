import { Fragment, useMemo, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { createBooking } from '../lib/bookings';
import toast from 'react-hot-toast';
import { isLoggedIn } from '../lib/auth';
import { useNavigate } from 'react-router-dom';

function fmtDate(iso) {
  try { return new Date(iso).toLocaleDateString(); } catch { return iso; }
}
function nightsBetween(ci, co) {
  try {
    const start = new Date(ci);
    const end = new Date(co);
    const ms = Math.max(0, end - start);
    return Math.max(1, Math.ceil(ms / (1000*60*60*24)));
  } catch { return 1; }
}

export default function BookingModal({ open, onClose, hotel, roomType, checkIn, checkOut }) {
  const [numGuests, setNumGuests] = useState(1);
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  const nights = useMemo(() => nightsBetween(checkIn, checkOut), [checkIn, checkOut]);
  const total = useMemo(() => Number(roomType?.base_price || 0) * nights, [roomType, nights]);

  const submit = async () => {
    if (!isLoggedIn()) { toast.error('Please login to book'); nav('/login'); return; }
    if (!checkIn || !checkOut) { toast.error('Select dates first'); return; }
    if (!hotel || !roomType) { toast.error('Pick a room type'); return; }

    setLoading(true);
    try {
      const res = await createBooking({
        hotel_id: hotel.id,
        room_type_id: roomType.id,
        check_in: checkIn,
        check_out: checkOut,
        num_guests: numGuests,
        total_amount: total,
        currency: 'USD'
      });
      const id = res.booking_id || res.id;
      toast.success(`Booked! ID #${id}`);
      onClose?.();
      nav('/my-bookings');
    } catch (e) {
      const msg = e?.normalized?.message || e?.response?.data?.error || 'Booking failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Transition show={open} as={Fragment}>
      <Dialog onClose={onClose} className="relative z-50">
        <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0" enterTo="opacity-100"
          leave="ease-in duration-150" leaveFrom="opacity-100" leaveTo="opacity-0">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
            leave="ease-in duration-150" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
            <Dialog.Panel className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl ring-1 ring-gray-200">
              <Dialog.Title className="text-lg font-semibold">Confirm your booking</Dialog.Title>
              <p className="text-sm text-gray-600 mt-1">{hotel?.name} — {roomType?.name}</p>

              <div className="mt-4 space-y-3 text-sm">
                <div className="flex justify-between"><span>Check-in</span><span>{fmtDate(checkIn)}</span></div>
                <div className="flex justify-between"><span>Check-out</span><span>{fmtDate(checkOut)}</span></div>
                <div className="flex justify-between"><span>Nights</span><span>{nights}</span></div>
                <div className="flex justify-between"><span>Price / night</span><span>${roomType?.base_price}</span></div>
                <div className="flex justify-between font-medium"><span>Total</span><span>${total.toFixed(2)}</span></div>
                <div className="flex items-center justify-between">
                  <label className="text-sm">Guests</label>
                  <input
                    type="number"
                    min={1}
                    max={roomType?.capacity || 1}
                    value={numGuests}
                    onChange={(e)=>setNumGuests(parseInt(e.target.value||'1',10))}
                    className="w-24 border rounded-md p-1.5 text-right focus:ring-2 focus:ring-black/10"
                  />
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-2">
                <button onClick={onClose} className="px-3 py-2 border rounded-md hover:bg-gray-50 disabled:opacity-50" disabled={loading}>
                  Cancel
                </button>
                <button
                  onClick={submit}
                  disabled={loading}
                  className="px-4 py-2 rounded-md bg-black text-white hover:bg-black/90 active:scale-[0.99] disabled:opacity-50"
                >
                  {loading ? 'Booking…' : 'Book Now'}
                </button>
              </div>
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
}
