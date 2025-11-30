"use client";

import React, { useState } from 'react';
import { useWallet } from '@/context/WalletContext';
import { Wallet, LogOut, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const WalletConnect = () => {
  const { isConnected, address, connect, disconnect, walletType } = useWallet();
  const [isOpen, setIsOpen] = useState(false);

  if (isConnected) {
    return (
      <div className="relative">
        <button
          onClick={disconnect}
          className="flex items-center gap-2 px-4 py-2 bg-neon-orchid/10 border border-neon-orchid/50 rounded-full text-neon-orchid hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/50 transition-all group"
          title="Click to Disconnect"
        >
          <Wallet className="w-4 h-4 group-hover:hidden" />
          <LogOut className="w-4 h-4 hidden group-hover:block" />
          <span className="font-mono text-sm">
            {address ? (address.length > 12 ? `${address.slice(0, 6)}...${address.slice(-4)}` : address) : 'Connected'}
          </span>
        </button>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-6 py-2 bg-white/5 border border-white/10 rounded-full text-white hover:bg-white/10 hover:border-white/30 transition-all group"
      >
        <Wallet className="w-4 h-4 group-hover:text-neon-orchid transition-colors" />
        <span className="text-sm font-medium">Connect Wallet</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute right-0 mt-2 w-56 bg-obsidian-core border border-white/10 rounded-xl shadow-xl overflow-hidden z-50"
          >
            <div className="p-2 space-y-1">
              <button
                onClick={() => { connect('cardano'); setIsOpen(false); }}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/5 transition-colors text-left group"
              >
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/30 transition-colors">
                  <span className="text-blue-400 text-xs font-bold">₳</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Cardano</p>
                  <p className="text-xs text-white/40">Nami, Eternl, Flint</p>
                </div>
              </button>
              
              <button
                onClick={() => { connect('ethereum'); setIsOpen(false); }}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/5 transition-colors text-left group"
              >
                <div className="w-8 h-8 rounded-full bg-orange-500/20 flex items-center justify-center group-hover:bg-orange-500/30 transition-colors">
                  <span className="text-orange-400 text-xs font-bold">Ξ</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">MetaMask</p>
                  <p className="text-xs text-white/40">Ethereum / EVM</p>
                </div>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
