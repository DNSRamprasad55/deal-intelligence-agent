import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Building2, BrainCircuit } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Deals Workspace', path: '/deals', icon: Briefcase },
    { name: 'Companies', path: '/companies', icon: Building2 },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800">
        <div className="p-2 bg-sky-600/20 text-sky-400 rounded-lg border border-sky-500/30">
          <BrainCircuit className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-slate-100 tracking-tight">Deal Intelligence</h1>
          <p className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Agent Platform</p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-sky-600/15 text-sky-400 border border-sky-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`
            }
          >
            <item.icon className="w-4 h-4" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Environment Footer */}
      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-500">
        <p>Phase 1 Foundation</p>
        <p className="text-[10px] text-slate-600 mt-0.5">PostgreSQL + Hindsight Architecture</p>
      </div>
    </aside>
  );
};
