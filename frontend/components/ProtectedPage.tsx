"use client";

import React from 'react';
import { useWallet } from '@/context/WalletContext';
import { ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

export const ProtectedPage = ({ children }: { children: React.ReactNode }) => {
  const { isConnected, connect } = useWallet();

  if (!isConnected) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-obsidian-core/80 backdrop-blur-xl border border-white/10 rounded-2xl p-8 text-center shadow-2xl"
        >
          <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <ShieldAlert className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-2xl font-bold font-orbitron mb-2 text-white">Access Restricted</h2>
          <p className="text-white/60 mb-8">
            Please connect your wallet to access the Sentinel Orchestrator Network.
          </p>
          
          <div className="space-y-3">
            <button
              onClick={() => connect('cardano')}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              Connect Cardano Wallet
            </button>
            <button
              onClick={() => connect('ethereum')}
              className="w-full py-3 px-4 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              Connect MetaMask
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return <>{children}</>;
};
