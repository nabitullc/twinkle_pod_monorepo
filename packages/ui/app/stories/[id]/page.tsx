'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { useChild } from '@/contexts/ChildContext';
import { Button } from '@/components/ui/Button';

interface StoryPage {
  text: string;
  image: string;
}

interface Story {
  story_id: string;
  title: string;
  pages: StoryPage[];
  age_range: string;
  category: string;
  tags: string[];
  moral?: string;
  duration_minutes: number;
  page_count: number;
}

export default function StoryReaderPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { selectedChild } = useChild();
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [direction, setDirection] = useState<'left' | 'right'>('right');

  useEffect(() => {
    fetchStory();
  }, [params.id]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') prevPage();
      if (e.key === 'ArrowRight') nextPage();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentPage, story]);

  useEffect(() => {
    if (story && user && selectedChild) {
      const timer = setTimeout(() => saveProgress(), 500);
      return () => clearTimeout(timer);
    }
  }, [currentPage, story, user, selectedChild]);

  const fetchStory = async () => {
    try {
      const { data } = await api.get(`/stories/${params.id}`);
      const storyResponse = await fetch(data.s3_url);
      const storyData = await storyResponse.json();
      setStory(storyData);
      
      if (user && selectedChild) {
        await api.post('/api/interaction', {
          child_id: selectedChild.child_id,
          story_id: params.id,
          event_type: 'view',
        });
      }
    } catch (error) {
      console.error('Failed to fetch story:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveProgress = async () => {
    if (!user || !selectedChild || !story) return;
    const percentage = ((currentPage + 1) / story.pages.length) * 100;
    try {
      await api.post('/api/progress', {
        child_id: selectedChild.child_id,
        story_id: story.story_id,
        paragraph_index: currentPage,
        percentage: Math.round(percentage),
        completed: currentPage === story.pages.length - 1,
      });
    } catch (error) {
      console.error('Failed to save progress:', error);
    }
  };

  const nextPage = useCallback(() => {
    if (!story || currentPage >= story.pages.length - 1) return;
    setDirection('right');
    setCurrentPage(p => p + 1);
  }, [story, currentPage]);

  const prevPage = useCallback(() => {
    if (currentPage <= 0) return;
    setDirection('left');
    setCurrentPage(p => p - 1);
  }, [currentPage]);

  const toggleFavorite = async () => {
    if (!user || !selectedChild || !story) return;
    try {
      await api.post('/api/interaction', {
        child_id: selectedChild.child_id,
        story_id: story.story_id,
        event_type: isFavorite ? 'unfavorite' : 'favorite',
      });
      setIsFavorite(!isFavorite);
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading story...</div>;
  }

  if (!story) {
    return <div className="min-h-screen flex items-center justify-center">Story not found</div>;
  }

  const progress = ((currentPage + 1) / story.pages.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center mb-4">
          <Button onClick={() => router.back()} variant="outline">← Back to Stories</Button>
          {user && selectedChild && (
            <Button onClick={toggleFavorite} variant={isFavorite ? 'primary' : 'outline'}>
              {isFavorite ? '★' : '☆'}
            </Button>
          )}
        </div>

        <div className="relative max-w-5xl mx-auto">
          <div className="relative aspect-[3/2] bg-white rounded-lg shadow-lg overflow-hidden">
            <div 
              key={currentPage}
              className={`absolute inset-0 animate-slide-${direction}`}
              style={{
                backgroundImage: `url(${story.pages[currentPage].image})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
                <p className="text-xl md:text-2xl leading-relaxed">
                  {story.pages[currentPage].text}
                </p>
              </div>
            </div>

            <button
              onClick={prevPage}
              disabled={currentPage === 0}
              className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/80 rounded-full flex items-center justify-center disabled:opacity-30 hover:bg-white transition"
            >
              ←
            </button>
            <button
              onClick={nextPage}
              disabled={currentPage === story.pages.length - 1}
              className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/80 rounded-full flex items-center justify-center disabled:opacity-30 hover:bg-white transition"
            >
              →
            </button>
          </div>

          <div className="mt-4 text-center text-gray-600">
            Page {currentPage + 1} / {story.pages.length}
          </div>

          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
