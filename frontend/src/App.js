import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [niches, setNiches] = useState([]);
  const [voices, setVoices] = useState({});
  const [selectedNiche, setSelectedNiche] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('female_calm');
  const [videoCount, setVideoCount] = useState(5);
  const [generatedVideos, setGeneratedVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentJob, setCurrentJob] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [recentVideos, setRecentVideos] = useState([]);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchNiches();
    fetchVoices();
    checkPipelineStatus();
    fetchRecentVideos();
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

  const fetchVoices = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/voices`);
      setVoices(response.data.voices);
    } catch (err) {
      console.error('Error fetching voices:', err);
    }
  };

  const checkPipelineStatus = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/test-pipeline`);
      setPipelineStatus(response.data);
    } catch (err) {
      console.error('Error checking pipeline status:', err);
    }
  };

  const fetchRecentVideos = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/list-videos?limit=10`);
      setRecentVideos(response.data.videos);
    } catch (err) {
      console.error('Error fetching recent videos:', err);
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
    setCurrentJob(null);

    try {
      const response = await axios.post(`${BACKEND_URL}/api/generate-videos`, {
        niche: selectedNiche,
        count: videoCount,
        voice_type: selectedVoice
      });
      
      setCurrentJob(response.data);
      
      // Start polling for job status
      pollJobStatus(response.data.job_id);
      
    } catch (err) {
      setError('Failed to start video generation. Please try again.');
      console.error('Error generating videos:', err);
      setLoading(false);
    }
  };

  const quickGenerate = async () => {
    if (!selectedNiche) {
      setError('Please select a niche');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/quick-generate`, {
        niche: selectedNiche,
        voice_type: selectedVoice
      });
      
      if (response.data.status === 'success') {
        setGeneratedVideos([response.data.video]);
        fetchRecentVideos(); // Refresh recent videos
      } else {
        setError('Quick generation failed');
      }
      
    } catch (err) {
      setError('Failed to generate video. Please try again.');
      console.error('Error in quick generation:', err);
    } finally {
      setLoading(false);
    }
  };

  const pollJobStatus = async (jobId) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/job-status/${jobId}`);
      const jobData = response.data;
      
      setCurrentJob(jobData);
      
      if (jobData.status === 'completed') {
        setGeneratedVideos(jobData.videos || []);
        setLoading(false);
        fetchRecentVideos(); // Refresh recent videos
      } else if (jobData.status === 'failed') {
        setError(jobData.error || 'Video generation failed');
        setLoading(false);
      } else {
        // Continue polling
        setTimeout(() => pollJobStatus(jobId), 3000);
      }
      
    } catch (err) {
      console.error('Error polling job status:', err);
      setLoading(false);
    }
  };

  const downloadVideo = async (videoId) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/download-video/${videoId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `video_${videoId}.mp4`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
    } catch (err) {
      console.error('Error downloading video:', err);
      setError('Failed to download video');
    }
  };

  const VideoCard = ({ video, showDownload = true }) => (
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
        <div className="flex flex-wrap gap-1 mb-3">
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
            {video.niche || 'Generated'}
          </span>
          {video.status && (
            <span className={`px-2 py-1 text-xs rounded ${
              video.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {video.status}
            </span>
          )}
        </div>
        {showDownload && video.status === 'success' && (
          <div className="flex space-x-2">
            <button 
              onClick={() => downloadVideo(video.id || video.video_id)}
              className="flex-1 bg-green-500 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-green-600 transition-colors"
            >
              Download MP4
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const JobStatusDisplay = () => {
    if (!currentJob) return null;
    
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">Generation Progress</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Status:</span>
            <span className={`font-medium ${
              currentJob.status === 'completed' ? 'text-green-600' :
              currentJob.status === 'failed' ? 'text-red-600' : 'text-blue-600'
            }`}>
              {currentJob.status}
            </span>
          </div>
          {currentJob.current_step && (
            <div className="flex justify-between">
              <span>Step:</span>
              <span className="font-medium">{currentJob.current_step}</span>
            </div>
          )}
          {currentJob.total_requested && (
            <div className="flex justify-between">
              <span>Progress:</span>
              <span className="font-medium">
                {currentJob.successful_videos || 0} / {currentJob.total_requested}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

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
                <p className="text-sm text-gray-600">Create viral shorts with AI in minutes! 🎬</p>
              </div>
            </div>
            {pipelineStatus && (
              <div className="text-right">
                <div className="text-sm text-gray-600">Pipeline Status</div>
                <div className="text-xs">
                  {pipelineStatus.pipeline_status === '✅ Ready for video generation' ? (
                    <span className="text-green-600 font-medium">🚀 Ready!</span>
                  ) : (
                    <span className="text-red-600 font-medium">⚠️ Issues detected</span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Generator Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Your Videos</h2>
          
          <div className="grid md:grid-cols-3 gap-6 mb-6">
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
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Voice Type
              </label>
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                disabled={loading}
              >
                {Object.entries(voices).map(([key, description]) => (
                  <option key={key} value={key}>
                    {description}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Videos
              </label>
              <select
                value={videoCount}
                onChange={(e) => setVideoCount(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                disabled={loading}
              >
                {[1, 2, 3, 4, 5].map((num) => (
                  <option key={num} value={num}>
                    {num} video{num > 1 ? 's' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={quickGenerate}
              disabled={loading || !selectedNiche}
              className="flex-1 bg-blue-500 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Generating...' : '⚡ Quick Generate (1 Video)'}
            </button>
            
            <button
              onClick={generateVideos}
              disabled={loading || !selectedNiche}
              className="flex-1 bg-red-500 text-white px-6 py-3 rounded-md font-medium hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Generating...' : `🎬 Generate ${videoCount} Videos`}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-md">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Job Status */}
        <JobStatusDisplay />

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="loading-spinner"></div>
            <p className="mt-4 text-gray-600">🎨 Creating your amazing videos...</p>
            <p className="text-sm text-gray-500">This may take 2-5 minutes depending on complexity</p>
          </div>
        )}

        {/* Generated Videos */}
        {generatedVideos.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                🎬 Your Generated Videos ({generatedVideos.length})
              </h2>
              <div className="text-sm text-gray-600">
                Niche: <span className="font-medium">{selectedNiche}</span>
              </div>
            </div>
            
            <div className="video-grid">
              {generatedVideos.map((video) => (
                <VideoCard key={video.id || video.video_id} video={video} />
              ))}
            </div>
          </div>
        )}

        {/* Recent Videos */}
        {recentVideos.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              📋 Recent Videos
            </h2>
            
            <div className="video-grid">
              {recentVideos.slice(0, 6).map((video) => (
                <VideoCard key={video.video_id} video={video} />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && generatedVideos.length === 0 && recentVideos.length === 0 && !error && (
          <div className="text-center py-12">
            <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Create Magic! ✨</h3>
            <p className="text-gray-600 mb-4">Select a niche and voice type to generate your first YouTube shorts</p>
            <div className="text-sm text-gray-500">
              <p>🎭 Choose from Comedy, Horror, or Motivational content</p>
              <p>🎤 Pick your preferred soothing voice</p>
              <p>🎬 Get ready-to-upload 9:16 videos!</p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2025 YouTube Shorts Generator. Built with ❤️ for creators.</p>
            <p className="text-sm mt-2">Powered by Edge TTS, MoviePy, and creative AI</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;