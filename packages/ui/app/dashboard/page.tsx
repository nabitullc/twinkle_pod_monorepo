'use client';

import { useState } from 'react';
import { useChild } from '@/contexts/ChildContext';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';

export default function DashboardPage() {
  const { children, refreshChildren } = useChild();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');

  const handleAddChild = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/children', { name, age: parseInt(age) });
      await refreshChildren();
      setIsModalOpen(false);
      setName('');
      setAge('');
    } catch (error) {
      console.error('Failed to add child:', error);
    }
  };

  const handleDeleteChild = async (childId: string) => {
    if (!confirm('Are you sure you want to delete this child profile?')) return;
    try {
      await api.delete(`/api/children/${childId}`);
      await refreshChildren();
    } catch (error) {
      console.error('Failed to delete child:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">👶 My Children</h1>
          <p className="text-gray-600">Manage your children&apos;s reading profiles</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} size="lg">
          ➕ Add Child
        </Button>
      </div>

      {children.length === 0 ? (
        <div className="text-center py-20 bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl border-2 border-dashed border-purple-200">
          <div className="text-6xl mb-4">👶</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">No children yet</h3>
          <p className="text-gray-600 mb-6">Add your first child to start their reading journey!</p>
          <Button onClick={() => setIsModalOpen(true)} size="lg">
            ✨ Add Your First Child
          </Button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {children.map((child) => (
            <div 
              key={child.child_id} 
              className="bg-white rounded-2xl shadow-sm hover:shadow-md transition-all p-6 border border-gray-100"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-2xl">
                    👧
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{child.name}</h3>
                    <p className="text-gray-600">Age {child.age}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteChild(child.child_id)}
                  className="text-red-400 hover:text-red-600 text-xl transition-colors"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
              <div className="pt-4 border-t border-gray-100">
                <p className="text-sm text-gray-500">Reading journey started! 📚</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="✨ Add Child">
        <form onSubmit={handleAddChild} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Child&apos;s Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="Emma"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Age</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="5"
              required
              min="3"
              max="12"
            />
          </div>
          <Button type="submit" className="w-full" size="lg">
            🎉 Add Child
          </Button>
        </form>
      </Modal>
    </div>
  );
}
