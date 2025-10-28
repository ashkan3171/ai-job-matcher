import { useState } from 'react'
import './App.css'

/* Your custom styles below */
// Define the type for the API response
interface MatchResult {
  similarity_score: number;
  matched_skill_percentage: number;
  matched_skills: string[];
  missing_skills: string[];
  extra_skills: string[];
  Status?: string;
}

function App() {
  const [jobText, setJobText] = useState('')
  const [resumeText, setResumeText] = useState('')
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const analyzeMatch = async () => {
    if (!jobText.trim() || !resumeText.trim()) {
      setError('Please enter both job description and resume')
      return
    }

    setLoading(true)
    setError(null)
    setMatchResult(null)

    try {
      const response = await fetch(`${API_URL}/cvjob-compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_text: jobText,
          resume_text: resumeText,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data: MatchResult = await response.json()
      setMatchResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze match')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Job Match Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            Find out how well your resume matches the job description
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Job Description Input */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Description
            </label>
            <textarea
              className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Paste the job description here..."
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
            />
          </div>

          {/* Resume Input */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Resume
            </label>
            <textarea
              className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Paste your resume here..."
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
          </div>
        </div>

        {/* Analyze Button */}
        <div className="text-center mb-8">
          <button
            onClick={analyzeMatch}
            disabled={loading}
            className={`px-8 py-4 rounded-lg text-white font-semibold text-lg transition-all ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 hover:shadow-xl transform hover:-translate-y-1'
            }`}
          >
            {loading ? 'Analyzing...' : 'Analyze Match'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Results */}
        {matchResult && (
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
              Match Analysis Results
            </h2>

            {/* Score Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {/* Semantic Similarity */}
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Semantic Similarity</h3>
                <div className="text-5xl font-bold">
                  {matchResult.similarity_score}%
                </div>
                <p className="text-blue-100 mt-2">Overall content match</p>
              </div>

              {/* Skills Match */}
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Skills Match</h3>
                <div className="text-5xl font-bold">
                  {matchResult.matched_skill_percentage}%
                </div>
                <p className="text-green-100 mt-2">Required skills you have</p>
              </div>
            </div>

            {/* Matched Skills */}
            {matchResult.matched_skills && matchResult.matched_skills.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  ✅ Skills You Have ({matchResult.matched_skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {matchResult.matched_skills.map((skill: string, index: number) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            {matchResult.missing_skills && matchResult.missing_skills.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  ⚠️ Skills You're Missing ({matchResult.missing_skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {matchResult.missing_skills.map((skill: string, index: number) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-red-100 text-red-800 rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Extra Skills */}
            {matchResult.extra_skills && matchResult.extra_skills.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  💡 Bonus Skills You Have ({matchResult.extra_skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {matchResult.extra_skills.map((skill: string, index: number) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App