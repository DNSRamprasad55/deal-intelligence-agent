import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({
  size = 'md',
  className = '',
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`flex items-center justify-center p-6 ${className}`}>
      <Loader2 className={`${sizes[size]} animate-spin text-sky-500`} />
    </div>
  );
};
