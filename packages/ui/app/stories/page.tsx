'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { api } from '@/lib/api';
import { StoryGridSkeleton } from '@/components/ui/LoadingSkeleton';

interface Story {
  story_id: string;
  title: string;
  age_range: string;
  categories: string[];
  duration_minutes: number;
  thumbnail_url: string;
}

export default function StoriesPage() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [ageRange, setAgeRange] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchStories();
  }, [category, ageRange]);

  const fetchStories = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (category) params.category = category;
      if (ageRange) params.age_range = ageRange;
      
      const { data } = await api.get('/stories/list', { params });
      setStories(data.stories || data);
    } catch (error) {
      console.error('Failed to fetch stories:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredStories = stories.filter(story =>
    story.title.toLowerCase().includes(search.toLowerCase())
  );

  const categories = ['animals', 'bedtime', 'family', 'friendship', 'emotions', 'learning', 'food'];
  const ageRanges = ['3-5', '4-6', '5-7', '7+'];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Browse Stories</h1>

      <div className="mb-8 space-y-4">
        <div className="flex flex-wrap gap-4">
          <select
            value={ageRange}
            onChange={(e) => setAgeRange(e.target.value)}
            className="px-4 py-2 border rounded-lg bg-white"
          >
            <option value="">All Ages</option>
            {ageRanges.map((age) => (
              <option key={age} value={age}>Age {age}</option>
            ))}
          </select>

          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-4 py-2 border rounded-lg bg-white"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat} className="capitalize">{cat}</option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Search stories..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] px-4 py-2 border rounded-lg"
          />
        </div>
      </div>

      {loading ? (
        <StoryGridSkeleton />
      ) : filteredStories.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No stories found. Try different filters.
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredStories.map((story) => (
            <Link key={story.story_id} href={`/stories/${story.story_id}`}>
              <div className="group cursor-pointer">
                <div className="relative aspect-[3/2] bg-gray-200 rounded-lg overflow-hidden mb-3 shadow-md group-hover:shadow-xl transition-shadow">
                  {story.thumbnail_url ? (
                    <Image
                      src={story.thumbnail_url}
                      alt={story.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-200 to-pink-200">
                      <span className="text-4xl">📚</span>
                    </div>
                  )}
                </div>
                <h3 className="font-semibold text-sm mb-1 line-clamp-2">{story.title}</h3>
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <span>Age {story.age_range}</span>
                  <span>{story.duration_minutes} min</span>
                </div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {story.categories.slice(0, 2).map((cat) => (
                    <span key={cat} className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
