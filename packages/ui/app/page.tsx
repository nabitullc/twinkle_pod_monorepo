import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-20">
        <div className="mb-6 text-6xl animate-bounce">✨</div>
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Every Child is the
          <span className="block bg-gradient-to-r from-purple-600 via-pink-500 to-amber-500 bg-clip-text text-transparent">
            Hero of Their Story
          </span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Magical bedtime stories that spark imagination and inspire dreams 🌙
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link href="/stories">
            <Button size="lg" className="shadow-lg hover:shadow-xl">
              🚀 Start Reading
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline">
              ✨ Create Account
            </Button>
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-8 mb-20">
        <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all border border-gray-100">
          <div className="text-5xl mb-4">📚</div>
          <h3 className="text-2xl font-bold mb-3 text-gray-900">100+ Stories</h3>
          <p className="text-gray-600 leading-relaxed">
            Bedtime tales, adventures, and moral stories for every mood
          </p>
        </div>
        
        <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all border border-gray-100">
          <div className="text-5xl mb-4">🎯</div>
          <h3 className="text-2xl font-bold mb-3 text-gray-900">Age-Perfect</h3>
          <p className="text-gray-600 leading-relaxed">
            Stories tailored for ages 3-10, growing with your child
          </p>
        </div>
        
        <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all border border-gray-100">
          <div className="text-5xl mb-4">⭐</div>
          <h3 className="text-2xl font-bold mb-3 text-gray-900">Track Progress</h3>
          <p className="text-gray-600 leading-relaxed">
            Save favorites and pick up right where you left off
          </p>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-br from-purple-100 via-pink-50 to-amber-50 rounded-3xl p-12 text-center shadow-lg border border-purple-200">
        <div className="text-5xl mb-4">🌟</div>
        <h2 className="text-4xl font-bold mb-4 text-gray-900">Ready to Begin?</h2>
        <p className="text-xl text-gray-700 mb-8 max-w-2xl mx-auto">
          Join thousands of families creating magical bedtime moments
        </p>
        <Link href="/login">
          <Button size="lg" variant="secondary" className="shadow-lg hover:shadow-xl">
            🎉 Get Started Free
          </Button>
        </Link>
      </div>
    </div>
  );
}
