/**
 * AuthForm Component Tests
 * Tests for the authentication form component (login/register)
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthForm } from '@/components/auth/AuthForm';

const mockOnSubmit = jest.fn();
const mockOnModeChange = jest.fn();

describe('AuthForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Login Mode', () => {
    it('should render login form correctly', () => {
      render(<AuthForm mode="login" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      expect(screen.getByText('Sign In')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
      expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
    });

    it('should validate email field', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="login" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      const emailInput = screen.getByLabelText('Email');
      await user.type(emailInput, 'invalid-email');
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      });
    });

    it('should validate password field', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="login" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      const passwordInput = screen.getByLabelText('Password');
      await user.type(passwordInput, '123');
      await user.tab();

      await waitFor(() => {
        expect(
          screen.getByText('Password must be at least 6 characters long')
        ).toBeInTheDocument();
      });
    });

    it('should submit login form with valid data', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="login" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      await user.type(screen.getByLabelText('Email'), 'user@example.com');
      await user.type(screen.getByLabelText('Password'), 'password123');
      await user.click(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          email: 'user@example.com',
          password: 'password123',
        });
      });
    });

    it('should switch to register mode', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="login" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      await user.click(screen.getByText('Sign up'));

      expect(mockOnModeChange).toHaveBeenCalledWith('register');
    });
  });

  describe('Register Mode', () => {
    it('should render register form correctly', () => {
      render(<AuthForm mode="register" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      expect(screen.getByText('Create Account')).toBeInTheDocument();
      expect(screen.getByLabelText('First Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Last Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
      expect(screen.getByText('Already have an account?')).toBeInTheDocument();
    });

    it('should validate name fields', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="register" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      const firstNameInput = screen.getByLabelText('First Name');
      await user.type(firstNameInput, 'A');
      await user.tab();

      await waitFor(() => {
        expect(
          screen.getByText('First name must be at least 2 characters long')
        ).toBeInTheDocument();
      });
    });

    it('should validate password confirmation', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="register" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      await user.type(screen.getByLabelText('Password'), 'password123');
      await user.type(screen.getByLabelText('Confirm Password'), 'different');
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
      });
    });

    it('should submit register form with valid data', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="register" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      await user.type(screen.getByLabelText('First Name'), 'John');
      await user.type(screen.getByLabelText('Last Name'), 'Doe');
      await user.type(screen.getByLabelText('Email'), 'john@example.com');
      await user.type(screen.getByLabelText('Password'), 'password123');
      await user.type(screen.getByLabelText('Confirm Password'), 'password123');
      await user.click(screen.getByRole('button', { name: 'Create Account' }));

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          email: 'john@example.com',
          password: 'password123',
          firstName: 'John',
          lastName: 'Doe',
        });
      });
    });

    it('should switch to login mode', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="register" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      await user.click(screen.getByText('Sign in'));

      expect(mockOnModeChange).toHaveBeenCalledWith('login');
    });
  });

  describe('Loading State', () => {
    it('should show loading state during submission', () => {
      render(
        <AuthForm
          mode="login"
          onSubmit={mockOnSubmit}
          onModeChange={mockOnModeChange}
          isLoading={true}
        />
      );

      const submitButton = screen.getByRole('button', { name: 'Signing In...' });
      expect(submitButton).toBeDisabled();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message', () => {
      render(
        <AuthForm
          mode="login"
          onSubmit={mockOnSubmit}
          onModeChange={mockOnModeChange}
          error="Invalid credentials"
        />
      );

      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should clear error on form change', async () => {
      const user = userEvent.setup();
      const mockClearError = jest.fn();

      render(
        <AuthForm
          mode="login"
          onSubmit={mockOnSubmit}
          onModeChange={mockOnModeChange}
          error="Invalid credentials"
          onClearError={mockClearError}
        />
      );

      await user.type(screen.getByLabelText('Email'), 'test');

      expect(mockClearError).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      render(<AuthForm mode="login" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      expect(screen.getByRole('form')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toHaveAttribute('type', 'email');
      expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password');
    });

    it('should announce form validation errors to screen readers', async () => {
      const user = userEvent.setup();

      render(<AuthForm mode="login" onSubmit={mockOnSubmit} onModeChange={mockOnModeChange} />);

      const emailInput = screen.getByLabelText('Email');
      await user.type(emailInput, 'invalid');
      await user.tab();

      await waitFor(() => {
        const errorMessage = screen.getByText('Please enter a valid email address');
        expect(errorMessage).toHaveAttribute('role', 'alert');
      });
    });
  });
});