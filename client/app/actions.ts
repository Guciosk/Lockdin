'use server'

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export async function signInAction(prevState: any, formData: FormData) {
  const email = formData.get('email');
  const password = formData.get('password');

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      return { type: 'error', message: data.message || 'Sign in failed' };
    }

    // Set the cookie using Response headers
    const response2 = new Response(null, {
      status: 200,
      headers: {
        'Set-Cookie': `token=${data.token}; Path=/; HttpOnly; Secure; SameSite=Lax`,
      },
    });
    
    redirect('/protected/dashboard');
  } catch (error) {
    return { type: 'error', message: 'An error occurred during sign in' };
  }
}

export async function signUpAction(prevState: any, formData: FormData) {
  const email = formData.get('email');
  const password = formData.get('password');
  const name = formData.get('name');

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });

    const data = await response.json();

    if (!response.ok) {
      return { type: 'error', message: data.message || 'Sign up failed' };
    }

    return { type: 'success', message: 'Registration successful! Please sign in.' };
  } catch (error) {
    return { type: 'error', message: 'An error occurred during registration' };
  }
}

export async function forgotPasswordAction(prevState: any, formData: FormData) {
  const email = formData.get('email');

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (!response.ok) {
      return { type: 'error', message: data.message || 'Password reset request failed' };
    }

    return { type: 'success', message: 'Password reset instructions sent to your email' };
  } catch (error) {
    return { type: 'error', message: 'An error occurred while processing your request' };
  }
}

export async function resetPasswordAction(prevState: any, formData: FormData) {
  const password = formData.get('password');
  const token = formData.get('token');

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password, token }),
    });

    const data = await response.json();

    if (!response.ok) {
      return { type: 'error', message: data.message || 'Password reset failed' };
    }

    return { type: 'success', message: 'Password reset successful! Please sign in.' };
  } catch (error) {
    return { type: 'error', message: 'An error occurred while resetting your password' };
  }
} 