import { useState } from 'react';

// Get API URL from environment variable or default to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [jobText, setJobText] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [uploadingPDF, setUploadingPDF] = useState(false); 

  // Handle PDF upload
  const handlePDFUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    setUploadingPDF(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/api/upload-pdf`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();

      // Fill the resume textarea with extracted text
      setResumeText(data.text);
      
      alert(`✅ PDF uploaded successfully!\n${data.page_count} page(s), ${data.char_count} characters extracted.`);

    } catch (error) {
      console.error('PDF upload error:', error);
      alert('❌ Failed to upload PDF. Please try again or paste text manually.');
    } finally {
      setUploadingPDF(false);
      // Reset file input
      event.target.value = '';
    }
  };

  // Function to call backend
  const handleCalculate = async () => { 
    if (!jobText.trim() || !resumeText.trim()) {
      alert("Please fill in both fields!");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // Call FastAPI backend
      console.log("Calling backend at:", API_URL); 

      const response = await fetch(`${API_URL}/cvjob-compare`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_text: jobText,
          resume_text: resumeText,
        }),
      });

      console.log("Response status:", response.status);

      const data = await response.json();
      console.log("Response data:", data);

      setResult(data); // Store the result
    } catch (error) {
      alert("Error connecting to backend. Make sure it's running!");
      console.error("Error details:", error);
    } finally {
      setLoading(false); // Hide loading state
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      {/* Header */}
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
          Job Match Analyzer
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Analyze how well your resume matches a job description
        </p>
        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          {/* Job Description */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Job Description
            </label>
            <textarea
              className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Paste the job description here..."
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
            />
          </div>
          {/* Resume */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Your Resume
            </label>
            {/* PDF Upload Button */}
            <div className="mb-3">
              <label className="inline-flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg cursor-pointer transition duration-200">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                {uploadingPDF ? 'Uploading...' : 'Upload PDF Resume'}
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf"
                  onChange={handlePDFUpload}
                  disabled={uploadingPDF}
                />
              </label>
              <span className="ml-3 text-sm text-gray-500">or paste text below</span>
            </div>

            {/* Resume Textarea */}
            <textarea
              className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Paste your resume here or upload PDF above..."
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
          </div>
          {/* Button */}
          <button 
            onClick={handleCalculate}
            disabled={loading}
            className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? "Calculating..." : "Calculate Match"}
          </button>
        </div>

        {/* Results Section */}
        {result && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Results</h2>
            
            {/* Scores */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Semantic Match</p>
                <p className="text-3xl font-bold text-blue-600">
                  {result.similarity_score}%
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Skills Match</p>
                <p className="text-3xl font-bold text-green-600">
                  {result.matched_skill_percentage}%
                </p>
              </div>
            </div>

            {/* Matched Skills */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                ✅ Matched Skills ({result.matched_skills.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.matched_skills.map((skill, index) => (
                  <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                ❌ Missing Skills ({result.missing_skills.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.missing_skills.map((skill, index) => (
                  <span key={index} className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Extra Skills */}
            {result.extra_skills.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">
                  ➕ Bonus Skills ({result.extra_skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.extra_skills.map((skill, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
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
  );
}

export default App;