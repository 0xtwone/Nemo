'use client';

import React from 'react';
import { usePrivy } from '@privy-io/react-auth';

export default function WalletConnect() {
  const { ready, authenticated, login } = usePrivy();

  const handleLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('登录出错：', error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      {authenticated ? (
        <p>Login Success</p>
      ) : (
        <button
          onClick={handleLogin}
          disabled={!ready}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {ready ? 'Login with Privy' : 'Privy initializing...'}
        </button>
      )}
    </div>
  );
} 