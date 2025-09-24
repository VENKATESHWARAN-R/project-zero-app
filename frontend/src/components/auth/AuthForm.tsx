'use client';

import { useState } from 'react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

export type AuthFormMode = 'login' | 'register';

interface AuthFormProps {
  initialMode?: AuthFormMode;
  onSuccess?: () => void;
  className?: string;
  showModeToggle?: boolean;
}

export function AuthForm({
  initialMode = 'login',
  onSuccess,
  className = '',
  showModeToggle = true
}: AuthFormProps) {
  const [mode, setMode] = useState<AuthFormMode>(initialMode);

  const handleModeToggle = () => {
    setMode(mode === 'login' ? 'register' : 'login');
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Mode Toggle Tabs */}
      {showModeToggle && (
        <div className="flex justify-center mb-6">
          <div className="flex bg-gray-100 rounded-lg p-1 w-full max-w-md mx-auto">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all ${
                mode === 'login'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all ${
                mode === 'register'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Create Account
            </button>
          </div>
        </div>
      )}

      {/* Form Content */}
      <div className="transition-all duration-300 ease-in-out">
        {mode === 'login' ? (
          <LoginForm
            onSuccess={onSuccess}
            className={showModeToggle ? 'shadow-none' : ''}
          />
        ) : (
          <RegisterForm
            onSuccess={onSuccess}
            className={showModeToggle ? 'shadow-none' : ''}
          />
        )}
      </div>

      {/* Additional Options */}
      {mode === 'login' && (
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            New to our store?{' '}
            <button
              onClick={handleModeToggle}
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Create an account
            </button>{' '}
            and get access to exclusive deals!
          </p>
        </div>
      )}

      {mode === 'register' && (
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Welcome back!{' '}
            <button
              onClick={handleModeToggle}
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Sign in to your account
            </button>{' '}
            to continue where you left off.
          </p>
        </div>
      )}
    </div>
  );
}

// Export individual forms for direct use
export { LoginForm, RegisterForm };