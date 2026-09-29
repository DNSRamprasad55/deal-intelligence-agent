import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'blue' | 'green' | 'red' | 'amber' | 'purple' | 'gray';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'gray',
  size = 'md',
  className = '',
}) => {
  const variants = {
    blue: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    red: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    gray: 'bg-slate-700/40 text-slate-300 border-slate-600/40',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 rounded',
    md: 'text-xs px-2.5 py-1 rounded-md',
  };

  return (
    <span
      className={`inline-flex items-center font-medium border ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {children}
    </span>
  );
};
