import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { healthService } from '../services/health';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { LogOut, User as UserIcon, Database, Cpu } from 'lucide-react';
import { HealthStatus } from '../types';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await healthService.getStatus();
        setHealth(res);
      } catch {
        // silent catch
      }
    };
    fetchHealth();
  }, []);

  const getHindsightBadgeVariant = (status?: string) => {
    if (status === 'available') return 'green';
    if (status === 'unavailable') return 'red';
    return 'amber';
  };

  return (
    <header className="h-16 bg-slate-900/90 border-b border-slate-800 px-6 flex items-center justify-between backdrop-blur-md sticky top-0 z-40">
      {/* System Status Indicators */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span>PostgreSQL:</span>
          <span className="text-slate-200 font-medium">
            {health?.database === 'connected' ? 'Connected' : 'Ready'}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-xs bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50">
          <Cpu className="w-3.5 h-3.5 text-sky-400" />
          <span className="text-slate-400">Hindsight Memory:</span>
          <Badge variant={getHindsightBadgeVariant(health?.hindsight)} size="sm">
            {health?.hindsight ? health.hindsight.toUpperCase() : 'NOT_CONFIGURED'}
          </Badge>
        </div>
      </div>

      {/* User Actions */}
      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <UserIcon className="w-4 h-4" />
            </div>
            <div className="text-left">
              <div className="text-xs font-semibold text-slate-200">{user.name}</div>
              <div className="text-[10px] text-slate-400 capitalize">{user.role.replace('_', ' ')}</div>
            </div>
          </div>
        )}

        <Button variant="ghost" size="sm" onClick={logout} className="text-slate-400 hover:text-rose-400">
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Logout</span>
        </Button>
      </div>
    </header>
  );
};
