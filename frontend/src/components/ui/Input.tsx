import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-medium text-slate-300 mb-1.5">
            {label}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={`w-full bg-slate-900 border ${
            error ? 'border-rose-500' : 'border-slate-700 focus:border-sky-500'
          } rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 ${
            error ? 'focus:ring-rose-500' : 'focus:ring-sky-500'
          } transition-colors ${className}`}
          {...props}
        />
        {error && <p className="mt-1 text-xs text-rose-400">{error}</p>}
      </div>
    );
  }
);
Input.displayName = 'Input';
