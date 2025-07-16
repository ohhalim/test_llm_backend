import React, { useState, useEffect } from 'react';
import { aiAPI } from '../services/api';
import './MedicalSearch.css';

const MedicalSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // 의료 지식 데이터베이스 통계 가져오기
    const fetchStats = async () => {
      try {
        const response = await aiAPI.getMedicalStats();
        setStats(response.data);
      } catch (err) {
        console.error('통계 조회 실패:', err);
      }
    };

    fetchStats();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('검색어를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await aiAPI.searchMedical(query.trim());
      setResults(response.data.results || []);
      
      if (response.data.results.length === 0) {
        setError('검색 결과가 없습니다.');
      }
    } catch (err) {
      console.error('검색 실패:', err);
      setError('검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const highlightQuery = (text, query) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  };

  return (
    <div className="medical-search">
      <div className="search-header">
        <h2>의료 지식 검색</h2>
        {stats && (
          <div className="stats-info">
            <span>총 {stats.total_documents}개의 의료 지식 데이터</span>
            <span className={`status ${stats.status}`}>{stats.status}</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="의료 관련 질문을 입력하세요... (예: 흉막천자, 당뇨병 치료, 고혈압 약물)"
            className="search-input"
          />
          <button 
            type="submit" 
            disabled={loading}
            className="search-button"
          >
            {loading ? '검색 중...' : '검색'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="search-results">
          <h3>검색 결과 ({results.length}개)</h3>
          {results.map((result, index) => (
            <div key={index} className="result-item">
              <div className="result-header">
                <div className="result-info">
                  <span className="result-type">
                    {result.metadata.type === 'medical_qa' ? 'Q&A' : '의료 시술'}
                  </span>
                  <span className="result-source">
                    {result.metadata.source || '의료 지식 데이터베이스'}
                  </span>
                  <span className="similarity-score">
                    관련도: {(result.similarity_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              
              <div className="result-content">
                <div 
                  dangerouslySetInnerHTML={{
                    __html: highlightQuery(result.content, query)
                  }}
                />
              </div>

              {result.metadata.domain && (
                <div className="result-metadata">
                  <span className="domain">분야: {result.metadata.domain}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="search-tips">
        <h4>검색 팁</h4>
        <ul>
          <li>구체적인 의료 용어를 사용하면 더 정확한 결과를 얻을 수 있습니다.</li>
          <li>증상, 치료법, 시술명 등 다양한 키워드로 검색해보세요.</li>
          <li>여러 단어를 조합하여 검색하면 관련성이 높은 결과를 찾을 수 있습니다.</li>
        </ul>
      </div>
    </div>
  );
};

export default MedicalSearch;