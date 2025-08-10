import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { createBooking } from '../lib/bookings';
import toast from 'react-hot-toast';
import { isLoggedIn } from '../lib/auth';
import { useNavigate } from 'react-router-dom';

export default function BookingModal({ open, onClose, hotel, roomType, checkIn, checkOut }) {
  const [numGuests, setNumGuests] = useState(1);
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  const submit = async () => {
    if (!isLoggedIn()) { toast.error('Please login to book'); nav('/login'); return; }
    if (!checkIn || !checkOut) { toast.error('Select dates first'); return; }
    setLoading(true);
    try {
      const res = await createBooking({
        hotel_id: hotel.id,
        room_type_id: roomType.id,
        check_in: checkIn,
        check_out: checkOut,
        num_guests: numGuests,
        total_amount: roomType.base_price, // simple
      });
      toast.success(`Booked! ID #${res.id}`);
      onClose();
      nav('/my-bookings');
    } catch (e) {
      const msg = e?.response?.data?.error || 'Booking failed';
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
          <div className="fixed inset-0 bg-black/30" />
        </Transition.Child>

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
            leave="ease-in duration-150" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
            <Dialog.Panel className="w-full max-w-md rounded-lg bg-white p-5 shadow-xl">
              <Dialog.Title className="text-lg font-semibold">Confirm Booking</Dialog.Title>
              <p className="text-sm text-gray-600 mt-1">{hotel.name} — {roomType.name}</p>

              <div className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between"><span>Check-in</span><span>{checkIn}</span></div>
                <div className="flex justify-between"><span>Check-out</span><span>{checkOut}</span></div>
                <div className="flex justify-between"><span>Price</span><span>${roomType.base_price}</span></div>
                <div className="flex items-center justify-between">
                  <label>Guests</label>
                  <input type="number" min={1} max={roomType.capacity} value={numGuests}
                         onChange={e=>setNumGuests(parseInt(e.target.value||'1',10))}
                         className="w-24 border rounded p-1 text-right"/>
                </div>
              </div>

              <div className="mt-5 flex justify-end gap-2">
                <button onClick={onClose} className="px-3 py-2 border rounded" disabled={loading}>Cancel</button>
                <button onClick={submit} disabled={loading}
                        className="px-3 py-2 bg-black text-white rounded disabled:opacity-50">
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
