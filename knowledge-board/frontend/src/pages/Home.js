import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="max-w-4xl mx-auto mt-8">
      {/* 히어로 섹션 */}
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          AI 기반 지식 공유 게시판
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          LangGraph와 RAG 기술을 활용하여 과거 게시글을 기반으로 
          지능적인 답변을 제공하는 지식 공유 플랫폼입니다.
        </p>
        
        <div className="space-x-4">
          <Link 
            to="/posts"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-medium"
          >
            게시글 보기
          </Link>
          {!isAuthenticated && (
            <Link 
              to="/register"
              className="border border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3 rounded-lg text-lg font-medium"
            >
              시작하기
            </Link>
          )}
        </div>
      </div>

      {/* 기능 소개 */}
      <div className="grid md:grid-cols-3 gap-8 py-16">
        <div className="text-center">
          <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">지식 공유</h3>
          <p className="text-gray-600">
            다양한 주제의 게시글을 작성하고 
            커뮤니티와 지식을 공유하세요.
          </p>
        </div>

        <div className="text-center">
          <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">AI 어시스턴트</h3>
          <p className="text-gray-600">
            과거 게시글을 학습한 AI가 
            관련된 질문에 지능적으로 답변합니다.
          </p>
        </div>

        <div className="text-center">
          <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">빠른 검색</h3>
          <p className="text-gray-600">
            RAG 기술을 활용하여 
            관련 정보를 빠르게 찾아드립니다.
          </p>
        </div>
      </div>

      {/* 기술 스택 */}
      <div className="bg-gray-50 rounded-lg p-8 mt-16">
        <h2 className="text-2xl font-bold text-center mb-8">사용된 기술</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="font-semibold">Backend</div>
            <div className="text-sm text-gray-600">FastAPI, PostgreSQL</div>
          </div>
          <div>
            <div className="font-semibold">Frontend</div>
            <div className="text-sm text-gray-600">React, Tailwind CSS</div>
          </div>
          <div>
            <div className="font-semibold">AI</div>
            <div className="text-sm text-gray-600">LangGraph, Gemini API</div>
          </div>
          <div>
            <div className="font-semibold">Vector DB</div>
            <div className="text-sm text-gray-600">ChromaDB</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;