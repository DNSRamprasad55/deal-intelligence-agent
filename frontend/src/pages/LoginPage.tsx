import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Button } from '../components/ui/Button';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { getErrorMessage } from '../services/api';
import { BrainCircuit } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('sales_rep');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await register({ name, email, password, role });
      } else {
        await login({ email, password });
      }
      navigate('/dashboard');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="p-3 bg-sky-600/20 text-sky-400 rounded-xl border border-sky-500/30 mb-3">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Deal Intelligence Agent</h1>
          <p className="text-xs text-slate-400 mt-1">Evidence-driven sales intelligence platform</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{isRegister ? 'Create Account' : 'Welcome Back'}</CardTitle>
            <CardDescription>
              {isRegister
                ? 'Register to start managing deals with persistent agent memory'
                : 'Enter your credentials to access your sales workspace'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && <ErrorAlert message={error} className="mb-4" />}

            <form onSubmit={handleSubmit} className="space-y-4">
              {isRegister && (
                <Input
                  label="Full Name"
                  placeholder="Jane Sales"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              )}

              <Input
                label="Email Address"
                type="email"
                placeholder="jane@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              {isRegister && (
                <Select
                  label="Role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  options={[
                    { value: 'sales_rep', label: 'Sales Representative' },
                    { value: 'manager', label: 'Sales Manager' },
                    { value: 'admin', label: 'Administrator' },
                  ]}
                />
              )}

              <Button type="submit" variant="primary" className="w-full" isLoading={loading}>
                {isRegister ? 'Register & Login' : 'Sign In'}
              </Button>
            </form>

            <div className="mt-6 text-center text-xs text-slate-400 border-t border-slate-700/50 pt-4">
              {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button
                type="button"
                onClick={() => {
                  setIsRegister(!isRegister);
                  setError('');
                }}
                className="text-sky-400 hover:underline font-medium ml-1"
              >
                {isRegister ? 'Sign In' : 'Create One'}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
