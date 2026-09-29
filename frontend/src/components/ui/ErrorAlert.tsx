import React from 'react';
import { AlertCircle } from 'lucide-react';

export const ErrorAlert: React.FC<{ message: string; className?: string }> = ({
  message,
  className = '',
}) => {
  if (!message) return null;

  return (
    <div className={`flex items-start gap-3 p-4 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-300 text-sm ${className}`}>
      <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
      <div>{message}</div>
    </div>
  );
};
