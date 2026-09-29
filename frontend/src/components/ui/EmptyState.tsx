import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Inbox,
  title,
  description,
  actionLabel,
  onAction,
}) => (
  <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-800/40 border border-dashed border-slate-700/60 rounded-xl">
    <div className="p-3 bg-slate-800 border border-slate-700/60 rounded-xl mb-3 text-slate-400">
      <Icon className="w-8 h-8" />
    </div>
    <h4 className="text-base font-medium text-slate-200">{title}</h4>
    <p className="text-xs text-slate-400 max-w-sm mt-1 mb-4">{description}</p>
    {actionLabel && onAction && (
      <Button variant="primary" size="sm" onClick={onAction}>
        {actionLabel}
      </Button>
    )}
  </div>
);
