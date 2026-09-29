import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  className = '',
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none cursor-pointer';

  const variants = {
    primary: 'bg-sky-600 text-white hover:bg-sky-700 focus:ring-sky-500 shadow-sm',
    secondary: 'bg-slate-800 text-slate-100 hover:bg-slate-700 focus:ring-slate-600 border border-slate-700',
    outline: 'border border-slate-700 text-slate-200 hover:bg-slate-800 focus:ring-slate-600',
    danger: 'bg-rose-600 text-white hover:bg-rose-700 focus:ring-rose-500 shadow-sm',
    ghost: 'text-slate-300 hover:bg-slate-800 hover:text-white focus:ring-slate-600',
  };

  const sizes = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2 gap-2',
    lg: 'text-base px-5 py-2.5 gap-2.5',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  );
};
