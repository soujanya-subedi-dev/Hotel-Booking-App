import { Link, Outlet } from 'react-router-dom';

export default function AdminLayout(){
  return (
    <div className="grid grid-cols-[220px_1fr] min-h-[70vh]">
      <aside className="border-r bg-white">
        <div className="p-4 font-semibold">Admin</div>
        <nav className="p-2 space-y-1">
          <Link className="block px-3 py-2 hover:bg-gray-100 rounded" to="/admin/hotels">Hotels</Link>
        </nav>
      </aside>
      <section className="p-4">
        <Outlet />
      </section>
    </div>
  );
}
