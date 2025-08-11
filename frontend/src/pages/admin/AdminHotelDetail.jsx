import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  adminGetHotel, adminUpdateHotel,
  adminAddImage, adminDeleteImage,
  adminCreateRT, adminUpdateRT, adminDeleteRT,
  adminCreateRoom, adminUpdateRoom, adminDeleteRoom,
  adminReportOcc, adminReportUsers
} from '../../lib/admin';

export default function AdminHotelDetail(){
  const { id } = useParams();
  const qc = useQueryClient();

  const { data, isLoading, error } = useQuery({ queryKey:['admin-hotel', id], queryFn: ()=>adminGetHotel(id) });
  const occ = useQuery({ queryKey:['occ', id],  queryFn: ()=>adminReportOcc(id) });
  const top = useQuery({ queryKey:['top-users', id], queryFn: ()=>adminReportUsers(id) });

  const updateHotel = useMutation({
    mutationFn: (b)=>adminUpdateHotel(id, b),
    onSuccess: ()=>{ toast.success('Updated'); qc.invalidateQueries(['admin-hotel', id]); }
  });
  const addImg = useMutation({
    mutationFn: (b)=>adminAddImage(id, b),
    onSuccess: ()=>{ toast.success('Image added'); qc.invalidateQueries(['admin-hotel', id]); }
  });

  const createRT = useMutation({ mutationFn: adminCreateRT,
    onSuccess: ()=>{ toast.success('Room type added'); qc.invalidateQueries(['admin-hotel', id]); }});
  const updateRT = useMutation({ mutationFn: ({rid,b})=>adminUpdateRT(rid,b),
    onSuccess: ()=>{ toast.success('Room type updated'); qc.invalidateQueries(['admin-hotel', id]); }});
  const deleteRT = useMutation({ mutationFn: adminDeleteRT,
    onSuccess: ()=>{ toast.success('Room type deleted'); qc.invalidateQueries(['admin-hotel', id]); }});

  const createRoom = useMutation({ mutationFn: adminCreateRoom,
    onSuccess: ()=>{ toast.success('Room added'); qc.invalidateQueries(['admin-hotel', id]); }});
  const updateRoom = useMutation({ mutationFn: ({rid,b})=>adminUpdateRoom(rid,b),
    onSuccess: ()=>{ toast.success('Room updated'); qc.invalidateQueries(['admin-hotel', id]); }});
  const deleteRoom = useMutation({ mutationFn: adminDeleteRoom,
    onSuccess: ()=>{ toast.success('Room deleted'); qc.invalidateQueries(['admin-hotel', id]); }});

  if (isLoading) return <p>Loading…</p>;
  if (error || !data?.hotel) return <p className="text-red-600">Not found.</p>;
  const h = data.hotel;

  const onHotelSave = (e)=>{
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    updateHotel.mutate({
      name: f.get('name'), city: f.get('city'), country: f.get('country'),
      address: f.get('address'), description: f.get('description'),
      star_rating: Number(f.get('star_rating')||0)
    });
  };
  const onAddImage = (e)=>{
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    addImg.mutate({ url: f.get('url'), alt_text: f.get('alt_text'), is_primary: Boolean(f.get('is_primary')) });
    e.currentTarget.reset();
  };
  const onAddRT = (e)=>{
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    createRT.mutate({
      hotel_id: Number(id),
      name: f.get('name'),
      capacity: Number(f.get('capacity')||2),
      base_price: Number(f.get('base_price')||0),
      description: f.get('description')||null
    });
    e.currentTarget.reset();
  };
  const onAddRoom = (e)=>{
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    createRoom.mutate({
      hotel_id: Number(id),
      room_type_id: Number(f.get('room_type_id')),
      room_number: f.get('room_number')
    });
    e.currentTarget.reset();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Manage: {h.name}</h1>

      {/* Hotel basics */}
      <form onSubmit={onHotelSave} className="grid sm:grid-cols-2 gap-3 bg-white p-3 rounded border">
        <div><label className="text-xs">Name</label><input name="name" defaultValue={h.name} className="border p-2 rounded w-full" /></div>
        <div><label className="text-xs">City</label><input name="city" defaultValue={h.city} className="border p-2 rounded w-full" /></div>
        <div><label className="text-xs">Country</label><input name="country" defaultValue={h.country} className="border p-2 rounded w-full" /></div>
        <div><label className="text-xs">Address</label><input name="address" defaultValue={h.address||''} className="border p-2 rounded w-full" /></div>
        <div><label className="text-xs">Stars</label><input type="number" name="star_rating" defaultValue={h.star_rating||0} className="border p-2 rounded w-full" /></div>
        <div className="sm:col-span-2"><label className="text-xs">Description</label><textarea name="description" defaultValue={h.description||''} className="border p-2 rounded w-full" /></div>
        <div className="sm:col-span-2"><button className="px-3 py-2 bg-black text-white rounded">Save</button></div>
      </form>

      {/* Occupancy & top users */}
      <div className="grid md:grid-cols-2 gap-3">
        <div className="bg-white p-3 rounded border">
          <div className="font-semibold mb-2">Occupancy</div>
          <pre className="text-sm">{JSON.stringify(occ.data||{}, null, 2)}</pre>
        </div>
        <div className="bg-white p-3 rounded border">
          <div className="font-semibold mb-2">Top Users</div>
          <pre className="text-sm">{JSON.stringify(top.data||[], null, 2)}</pre>
        </div>
      </div>

      {/* Images */}
      <div className="bg-white p-3 rounded border">
        <div className="font-semibold mb-2">Images</div>
        <form onSubmit={onAddImage} className="flex flex-wrap gap-2 items-end mb-3">
          <input name="url" placeholder="Image URL" className="border p-2 rounded w-72" required />
          <input name="alt_text" placeholder="Alt text" className="border p-2 rounded w-56" />
          <label className="text-sm flex items-center gap-1"><input type="checkbox" name="is_primary" /> Primary</label>
          <button className="px-3 py-2 border rounded">Add</button>
        </form>
        <div className="flex gap-2 overflow-x-auto">
          {data.images.map(img=>(
            <div key={img.id} className="border rounded p-2">
              <img src={img.url} alt={img.alt_text||''} className="h-24 rounded"/>
              <div className="text-xs mt-1">{img.is_primary ? 'Primary' : ''}</div>
              <button
                onClick={()=>adminDeleteImage(img.id).then(()=>{toast.success('Deleted'); qc.invalidateQueries(['admin-hotel', id]);})}
                className="text-xs mt-1 px-2 py-1 border rounded">Delete</button>
            </div>
          ))}
        </div>
      </div>

      {/* Room Types */}
      <div className="bg-white p-3 rounded border">
        <div className="font-semibold mb-2">Room Types</div>
        <form onSubmit={onAddRT} className="flex flex-wrap gap-2 items-end mb-3">
          <input name="name" placeholder="Name" className="border p-2 rounded" required />
          <input name="capacity" type="number" placeholder="Cap" className="border p-2 rounded w-24" defaultValue={2}/>
          <input name="base_price" type="number" step="0.01" placeholder="Price" className="border p-2 rounded w-28" required />
          <button className="px-3 py-2 border rounded">Add</button>
        </form>
        <div className="grid md:grid-cols-2 gap-2">
          {data.room_types.map(rt=>(
            <div key={rt.id} className="border rounded p-2">
              <div className="font-medium">{rt.name}</div>
              <div className="text-sm text-gray-600">Cap {rt.capacity} · ${rt.base_price}</div>
              <div className="mt-2 flex gap-2">
                <button onClick={()=>updateRT.mutate({ rid: rt.id, b: { active: !rt.active }})} className="px-2 py-1 border rounded text-xs">
                  {rt.active ? 'Disable' : 'Enable'}
                </button>
                <button onClick={()=>deleteRT.mutate(rt.id)} className="px-2 py-1 border rounded text-xs">Delete</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Rooms */}
      <div className="bg-white p-3 rounded border">
        <div className="font-semibold mb-2">Rooms</div>
        <form onSubmit={onAddRoom} className="flex flex-wrap gap-2 items-end mb-3">
          <select name="room_type_id" className="border p-2 rounded" required>
            {data.room_types.map(rt=> <option key={rt.id} value={rt.id}>{rt.name}</option>)}
          </select>
          <input name="room_number" placeholder="Room no." className="border p-2 rounded" required />
          <button className="px-3 py-2 border rounded">Add</button>
        </form>
        <div className="grid md:grid-cols-2 gap-2">
          {data.rooms.map(r=>(
            <div key={r.id} className="border rounded p-2">
              <div className="font-medium">#{r.room_number}</div>
              <div className="text-sm text-gray-600">{r.status}</div>
              <div className="mt-2 flex gap-2">
                <button onClick={()=>updateRoom.mutate({ rid: r.id, b: { status: r.status === 'available' ? 'maintenance' : 'available' }})}
                        className="px-2 py-1 border rounded text-xs">Toggle Status</button>
                <button onClick={()=>deleteRoom.mutate(r.id)} className="px-2 py-1 border rounded text-xs">Delete</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
