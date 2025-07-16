import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { postsAPI } from '../services/api';

const PostList = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    size: 10,
    total: 0,
    totalPages: 0,
  });

  useEffect(() => {
    fetchPosts(pagination.page);
  }, [pagination.page]);

  const fetchPosts = async (page = 1) => {
    try {
      setLoading(true);
      const response = await postsAPI.getPosts(page, pagination.size);
      const data = response.data;
      
      setPosts(data.posts);
      setPagination({
        page: data.page,
        size: data.size,
        total: data.total,
        totalPages: data.total_pages,
      });
    } catch (error) {
      setError('게시글을 불러오는데 실패했습니다.');
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">게시글을 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mt-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">게시글 목록</h1>
        <span className="text-gray-600">총 {pagination.total}개의 게시글</span>
      </div>

      {posts.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600 mb-4">아직 게시글이 없습니다.</p>
          <Link 
            to="/posts/new" 
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          >
            첫 번째 게시글 작성하기
          </Link>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {posts.map((post) => (
              <div 
                key={post.id} 
                className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <Link 
                    to={`/posts/${post.id}`}
                    className="text-xl font-semibold text-blue-600 hover:text-blue-800"
                  >
                    {post.title}
                  </Link>
                  <span className="text-sm text-gray-500">
                    {formatDate(post.created_at)}
                  </span>
                </div>
                
                <p className="text-gray-600 mb-3 line-clamp-3">
                  {post.content.length > 150 
                    ? `${post.content.substring(0, 150)}...` 
                    : post.content
                  }
                </p>
                
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>작성자: {post.author.username}</span>
                  <Link 
                    to={`/posts/${post.id}`}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    자세히 보기 →
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* 페이지네이션 */}
          {pagination.totalPages > 1 && (
            <div className="flex justify-center mt-8">
              <div className="flex space-x-2">
                {pagination.page > 1 && (
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100"
                  >
                    이전
                  </button>
                )}
                
                {Array.from({ length: pagination.totalPages }, (_, i) => i + 1)
                  .filter(page => 
                    page === 1 || 
                    page === pagination.totalPages || 
                    Math.abs(page - pagination.page) <= 2
                  )
                  .map((page, index, array) => (
                    <React.Fragment key={page}>
                      {index > 0 && array[index - 1] !== page - 1 && (
                        <span className="px-3 py-1">...</span>
                      )}
                      <button
                        onClick={() => handlePageChange(page)}
                        className={`px-3 py-1 border rounded ${
                          page === pagination.page
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100'
                        }`}
                      >
                        {page}
                      </button>
                    </React.Fragment>
                  ))
                }
                
                {pagination.page < pagination.totalPages && (
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100"
                  >
                    다음
                  </button>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PostList;