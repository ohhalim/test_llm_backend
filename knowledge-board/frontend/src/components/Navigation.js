import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* 로고/홈 링크 */}
          <Link to="/" className="text-xl font-bold hover:text-blue-200">
            지식 공유 게시판
          </Link>

          {/* 네비게이션 메뉴 */}
          <div className="flex items-center space-x-4">
            <Link 
              to="/posts" 
              className="hover:text-blue-200 transition-colors"
            >
              게시글
            </Link>
            <Link 
              to="/medical-search" 
              className="hover:text-blue-200 transition-colors"
            >
              의료 지식 검색
            </Link>

            {isAuthenticated ? (
              <>
                <Link 
                  to="/posts/new" 
                  className="bg-blue-500 hover:bg-blue-400 px-4 py-2 rounded transition-colors"
                >
                  글쓰기
                </Link>
                <span className="text-blue-200">
                  안녕하세요, {user?.username}님
                </span>
                <button
                  onClick={handleLogout}
                  className="hover:text-blue-200 transition-colors"
                >
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  className="hover:text-blue-200 transition-colors"
                >
                  로그인
                </Link>
                <Link 
                  to="/register" 
                  className="bg-blue-500 hover:bg-blue-400 px-4 py-2 rounded transition-colors"
                >
                  회원가입
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;