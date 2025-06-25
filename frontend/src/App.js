import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [niches, setNiches] = useState([]);
  const [selectedNiche, setSelectedNiche] = useState('');
  const [generatedVideos, setGeneratedVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchNiches();
  }, []);

  const fetchNiches = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/niches`);
      setNiches(response.data.niches);
    } catch (err) {
      setError('Failed to load niches');
      console.error('Error fetching niches:', err);
    }
  };

  const generateVideos = async () => {
    if (!selectedNiche) {
      setError('Please select a niche');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedVideos([]);

    try {
      const response = await axios.post(`${BACKEND_URL}/api/generate-videos`, {
        niche: selectedNiche
      });
      
      setGeneratedVideos(response.data.videos);
    } catch (err) {
      setError('Failed to generate videos. Please try again.');
      console.error('Error generating videos:', err);
    } finally {
      setLoading(false);
    }
  };

  const VideoCard = ({ video }) => (
    <div className="video-card bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="video-aspect-ratio bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center">
        <div className="text-white text-center p-4">
          <div className="w-12 h-12 mx-auto mb-2 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm font-medium">9:16 Video</p>
          <p className="text-xs opacity-75">{video.duration}s</p>
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">{video.title}</h3>
        <p className="text-sm text-gray-600 mb-3 line-clamp-3">{video.description}</p>
        <div className="flex space-x-2">
          <button className="flex-1 bg-red-500 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-600 transition-colors">
            Download
          </button>
          <button className="flex-1 bg-gray-200 text-gray-800 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-300 transition-colors">
            Preview
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">YouTube Shorts Generator</h1>
                <p className="text-sm text-gray-600">Create viral shorts in seconds</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Generator Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Your Videos</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Your Niche
              </label>
              <select
                value={selectedNiche}
                onChange={(e) => setSelectedNiche(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                disabled={loading}
              >
                <option value="">Choose a niche...</option>
                {niches.map((niche) => (
                  <option key={niche} value={niche}>
                    {niche}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={generateVideos}
                disabled={loading || !selectedNiche}
                className="w-full bg-red-500 text-white px-6 py-2 rounded-md font-medium hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Generating...' : 'Generate 5 Videos'}
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-md">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="loading-spinner"></div>
            <p className="mt-4 text-gray-600">Generating your amazing videos...</p>
            <p className="text-sm text-gray-500">This may take a few moments</p>
          </div>
        )}

        {/* Generated Videos */}
        {generatedVideos.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Generated Videos ({generatedVideos.length})
              </h2>
              <div className="text-sm text-gray-600">
                Niche: <span className="font-medium">{selectedNiche}</span>
              </div>
            </div>
            
            <div className="video-grid">
              {generatedVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && generatedVideos.length === 0 && !error && (
          <div className="text-center py-12">
            <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Create</h3>
            <p className="text-gray-600 mb-4">Select a niche and generate your first set of YouTube shorts</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2025 YouTube Shorts Generator. Built with ❤️ for creators.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;