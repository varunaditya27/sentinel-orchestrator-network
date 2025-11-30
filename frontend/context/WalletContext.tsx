"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type WalletType = 'cardano' | 'ethereum' | null;

interface WalletContextType {
  isConnected: boolean;
  address: string | null;
  walletType: WalletType;
  connect: (type: 'cardano' | 'ethereum') => Promise<void>;
  disconnect: () => void;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export const WalletProvider = ({ children }: { children: ReactNode }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [address, setAddress] = useState<string | null>(null);
  const [walletType, setWalletType] = useState<WalletType>(null);

  // Load state from local storage on mount
  useEffect(() => {
    const storedConnected = localStorage.getItem('walletConnected');
    const storedType = localStorage.getItem('walletType') as WalletType;
    
    if (storedConnected === 'true' && storedType) {
      // Attempt to reconnect silently if possible, or just restore state
      // For MVP, we just restore state. In prod, verify connection.
      setIsConnected(true);
      setWalletType(storedType);
      setAddress(localStorage.getItem('walletAddress'));
    }
  }, []);

  const connect = async (type: 'cardano' | 'ethereum') => {
    try {
      if (type === 'ethereum') {
        if (typeof window !== 'undefined' && (window as any).ethereum) {
          const accounts = await (window as any).ethereum.request({ method: 'eth_requestAccounts' });
          if (accounts.length > 0) {
            setAddress(accounts[0]);
            setIsConnected(true);
            setWalletType('ethereum');
            localStorage.setItem('walletConnected', 'true');
            localStorage.setItem('walletType', 'ethereum');
            localStorage.setItem('walletAddress', accounts[0]);
          }
        } else {
          alert("MetaMask not installed!");
        }
      } else if (type === 'cardano') {
        if (typeof window !== 'undefined' && (window as any).cardano) {
          // Check for available wallets (nami, eternl, flint, etc.)
          const cardano = (window as any).cardano;
          const walletName = cardano.nami ? 'nami' : (cardano.eternl ? 'eternl' : null);
          
          if (walletName) {
            const api = await cardano[walletName].enable();
            const rawAddress = await api.getChangeAddress();
            // In a real app, decode the address (bech32). For now, use a truncated raw or mock.
            // Since we don't have cardano-serialization-lib installed, we'll just store "Connected (Cardano)"
            // or try to use the raw hex.
            setAddress("addr_..." + rawAddress.slice(0, 8)); 
            setIsConnected(true);
            setWalletType('cardano');
            localStorage.setItem('walletConnected', 'true');
            localStorage.setItem('walletType', 'cardano');
            localStorage.setItem('walletAddress', "addr_..." + rawAddress.slice(0, 8));
          } else {
            alert("No supported Cardano wallet found (Nami, Eternl).");
          }
        } else {
          alert("Cardano wallet not found!");
        }
      }
    } catch (error) {
      console.error("Connection failed:", error);
      alert("Failed to connect wallet.");
    }
  };

  const disconnect = () => {
    setIsConnected(false);
    setAddress(null);
    setWalletType(null);
    localStorage.removeItem('walletConnected');
    localStorage.removeItem('walletType');
    localStorage.removeItem('walletAddress');
  };

  return (
    <WalletContext.Provider value={{ isConnected, address, walletType, connect, disconnect }}>
      {children}
    </WalletContext.Provider>
  );
};

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
};
