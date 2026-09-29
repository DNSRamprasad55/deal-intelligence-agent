import React from 'react';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className = '', id, rows = 3, ...props }, ref) => {
    const textareaId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={textareaId} className="block text-xs font-medium text-slate-300 mb-1.5">
            {label}
          </label>
        )}
        <textarea
          id={textareaId}
          ref={ref}
          rows={rows}
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
Textarea.displayName = 'Textarea';
