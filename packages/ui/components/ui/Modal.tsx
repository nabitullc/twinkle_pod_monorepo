'use client';

import { ReactNode } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export const Modal = ({ isOpen, onClose, title, children }: ModalProps) => {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm animate-in fade-in duration-200" 
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl border border-gray-100 animate-in zoom-in-95 duration-200" 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-gray-600 text-2xl w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-all"
          >
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};
