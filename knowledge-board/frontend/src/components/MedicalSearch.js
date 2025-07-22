import React, { useState, useEffect } from 'react';
import { aiAPI } from '../services/api';
import './MedicalSearch.css';

const MedicalSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [qaAnswer, setQaAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);
  const [ragHealth, setRagHealth] = useState(null);
  const [searchMode, setSearchMode] = useState('search'); // 'search' 또는 'qa'

  useEffect(() => {
    // 의료 지식 데이터베이스 통계 및 RAG 헬스 체크
    const fetchData = async () => {
      try {
        const [statsResponse, healthResponse] = await Promise.all([
          aiAPI.getMedicalStats(),
          aiAPI.getRagHealth()
        ]);
        setStats(statsResponse.data);
        setRagHealth(healthResponse.data);
      } catch (err) {
        console.error('데이터 조회 실패:', err);
      }
    };

    fetchData();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('검색어 또는 질문을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);
    setQaAnswer(null);

    try {
      if (searchMode === 'search') {
        // 유사도 검색
        const response = await aiAPI.searchMedical(query.trim());
        setResults(response.data.results || []);
        
        if (response.data.results.length === 0) {
          setError('검색 결과가 없습니다.');
        }
      } else {
        // RAG 기반 질의응답
        const response = await aiAPI.medicalQA(query.trim());
        setQaAnswer(response.data);
        
        if (response.data.error) {
          setError(response.data.error);
        }
      }
    } catch (err) {
      console.error('요청 실패:', err);
      if (err.response?.status === 503) {
        setError('RAG 시스템이 초기화되지 않았습니다. GEMINI_API_KEY 설정이 필요합니다.');
      } else {
        setError(searchMode === 'search' ? '검색 중 오류가 발생했습니다.' : '질의응답 중 오류가 발생했습니다.');
      }
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
        <h2>의료 지식 RAG 시스템</h2>
        <div className="system-info">
          {stats && (
            <div className="stats-info">
              <span>총 {stats.total_documents}개의 의료 지식 데이터</span>
              <span className={`status ${stats.status}`}>{stats.status}</span>
              {ragHealth && (
                <span className={`rag-status ${ragHealth.overall ? 'active' : 'inactive'}`}>
                  RAG: {ragHealth.overall ? '활성' : '비활성'}
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="search-mode-selector">
        <div className="mode-tabs">
          <button 
            className={`mode-tab ${searchMode === 'search' ? 'active' : ''}`}
            onClick={() => setSearchMode('search')}
          >
            문서 검색
          </button>
          <button 
            className={`mode-tab ${searchMode === 'qa' ? 'active' : ''}`}
            onClick={() => setSearchMode('qa')}
            disabled={!ragHealth?.overall}
          >
            AI 질의응답 {!ragHealth?.overall && '(비활성)'}
          </button>
        </div>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              searchMode === 'search' 
                ? "의료 용어로 검색하세요... (예: 흉막천자, 당뇨병 치료)"
                : "의료 관련 질문을 하세요... (예: 흉막천자는 어떤 시술인가요?)"
            }
            className="search-input"
          />
          <button 
            type="submit" 
            disabled={loading || (searchMode === 'qa' && !ragHealth?.overall)}
            className="search-button"
          >
            {loading ? (searchMode === 'search' ? '검색 중...' : '답변 생성 중...') : 
             (searchMode === 'search' ? '검색' : 'AI 질문')}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* RAG 질의응답 결과 */}
      {qaAnswer && (
        <div className="qa-result">
          <div className="qa-header">
            <h3>AI 답변</h3>
            <span className="qa-type">LangChain RAG 기반</span>
          </div>
          
          <div className="qa-content">
            <div className="question">
              <strong>질문:</strong> {qaAnswer.question}
            </div>
            <div className="answer">
              <strong>답변:</strong>
              <div className="answer-text">{qaAnswer.answer}</div>
            </div>
          </div>

          {qaAnswer.source_documents && qaAnswer.source_documents.length > 0 && (
            <div className="source-documents">
              <h4>참고 문서 ({qaAnswer.total_sources}개)</h4>
              {qaAnswer.source_documents.map((doc, index) => (
                <div key={index} className="source-item">
                  <div className="source-header">
                    <span className="source-type">{doc.metadata.type || '의료 문서'}</span>
                    <span className="source-name">{doc.metadata.source || '의료 지식 데이터베이스'}</span>
                  </div>
                  <div className="source-content">
                    <div 
                      dangerouslySetInnerHTML={{
                        __html: highlightQuery(doc.content, query)
                      }}
                    />
                  </div>
                  {doc.metadata.domain && (
                    <div className="source-metadata">
                      <span className="domain">분야: {doc.metadata.domain}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 문서 검색 결과 */}
      {results.length > 0 && (
        <div className="search-results">
          <h3>검색 결과 ({results.length}개)</h3>
          {results.map((result, index) => (
            <div key={index} className="result-item">
              <div className="result-header">
                <div className="result-info">
                  <span className="result-type">
                    {result.metadata?.type === 'medical_qa' ? 'Q&A' : '의료 시술'}
                  </span>
                  <span className="result-source">
                    {result.metadata?.source || result.source || '의료 지식 데이터베이스'}
                  </span>
                  <span className="similarity-score">
                    관련도: {((result.similarity_score || result.score || 0) * 100).toFixed(1)}%
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

              {(result.metadata?.domain || result.domain) && (
                <div className="result-metadata">
                  <span className="domain">분야: {result.metadata?.domain || result.domain}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="search-tips">
        <h4>사용 팁</h4>
        {searchMode === 'search' ? (
          <ul>
            <li><strong>문서 검색:</strong> 구체적인 의료 용어로 유사 문서를 찾습니다.</li>
            <li>키워드 예시: "흉막천자", "당뇨병 치료", "고혈압 약물"</li>
            <li>여러 용어를 조합하면 더 정확한 결과를 얻을 수 있습니다.</li>
          </ul>
        ) : (
          <ul>
            <li><strong>AI 질의응답:</strong> 자연어로 질문하면 AI가 의료 지식을 바탕으로 답변합니다.</li>
            <li>질문 예시: "흉막천자는 어떤 시술인가요?", "당뇨병 치료법에는 무엇이 있나요?"</li>
            <li>참고 문서와 함께 상세한 답변을 제공합니다.</li>
            {!ragHealth?.overall && (
              <li className="warning">⚠️ RAG 시스템이 비활성 상태입니다. GEMINI_API_KEY 설정이 필요합니다.</li>
            )}
          </ul>
        )}
      </div>
    </div>
  );
};

export default MedicalSearch;