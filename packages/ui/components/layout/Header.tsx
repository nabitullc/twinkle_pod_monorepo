'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useChild } from '@/contexts/ChildContext';
import { Button } from '@/components/ui/Button';

export const Header = () => {
  const { user, logout } = useAuth();
  const { children, selectedChild, selectChild } = useChild();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 group">
            <span className="text-3xl">✨</span>
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent">
              TwinklePod
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/stories" className="text-gray-700 hover:text-purple-600 font-medium transition-colors">
              📚 Stories
            </Link>
            
            {user ? (
              <>
                <Link href="/library" className="text-gray-700 hover:text-purple-600 font-medium transition-colors">
                  ⭐ Library
                </Link>
                <Link href="/dashboard" className="text-gray-700 hover:text-purple-600 font-medium transition-colors">
                  👶 Dashboard
                </Link>
                
                {children.length > 0 && (
                  <select
                    value={selectedChild?.child_id || ''}
                    onChange={(e) => {
                      const child = children.find(c => c.child_id === e.target.value);
                      if (child) selectChild(child);
                    }}
                    className="border-2 border-purple-200 rounded-xl px-4 py-2 bg-purple-50 text-purple-900 font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                  >
                    {children.map(child => (
                      <option key={child.child_id} value={child.child_id}>
                        👧 {child.name}
                      </option>
                    ))}
                  </select>
                )}
                
                <Button onClick={logout} variant="outline" size="sm">
                  Logout
                </Button>
              </>
            ) : (
              <Link href="/login">
                <Button size="sm">Login</Button>
              </Link>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-2xl text-gray-700 hover:text-purple-600 transition-colors"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden mt-4 pb-4 space-y-3 border-t border-gray-100 pt-4">
            <Link href="/stories" className="block text-gray-700 hover:text-purple-600 font-medium py-2">
              📚 Stories
            </Link>
            {user ? (
              <>
                <Link href="/library" className="block text-gray-700 hover:text-purple-600 font-medium py-2">
                  ⭐ Library
                </Link>
                <Link href="/dashboard" className="block text-gray-700 hover:text-purple-600 font-medium py-2">
                  👶 Dashboard
                </Link>
                {children.length > 0 && (
                  <select
                    value={selectedChild?.child_id || ''}
                    onChange={(e) => {
                      const child = children.find(c => c.child_id === e.target.value);
                      if (child) selectChild(child);
                    }}
                    className="w-full border-2 border-purple-200 rounded-xl px-4 py-2 bg-purple-50 text-purple-900 font-medium"
                  >
                    {children.map(child => (
                      <option key={child.child_id} value={child.child_id}>
                        👧 {child.name}
                      </option>
                    ))}
                  </select>
                )}
                <Button onClick={logout} variant="outline" className="w-full">
                  Logout
                </Button>
              </>
            ) : (
              <Link href="/login" className="block">
                <Button className="w-full">Login</Button>
              </Link>
            )}
          </nav>
        )}
      </div>
    </header>
  );
};
