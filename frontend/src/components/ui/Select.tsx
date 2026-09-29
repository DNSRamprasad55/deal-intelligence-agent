import React from 'react';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, error, className = '', id, ...props }, ref) => {
    const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={selectId} className="block text-xs font-medium text-slate-300 mb-1.5">
            {label}
          </label>
        )}
        <select
          id={selectId}
          ref={ref}
          className={`w-full bg-slate-900 border ${
            error ? 'border-rose-500' : 'border-slate-700 focus:border-sky-500'
          } rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:ring-1 ${
            error ? 'focus:ring-rose-500' : 'focus:ring-sky-500'
          } transition-colors ${className}`}
          {...props}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-100">
              {opt.label}
            </option>
          ))}
        </select>
        {error && <p className="mt-1 text-xs text-rose-400">{error}</p>}
      </div>
    );
  }
);
Select.displayName = 'Select';
