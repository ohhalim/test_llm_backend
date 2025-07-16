import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { postsAPI } from '../services/api';

const PostDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      setLoading(true);
      const response = await postsAPI.getPost(id);
      setPost(response.data);
    } catch (error) {
      setError('게시글을 불러오는데 실패했습니다.');
      console.error('Error fetching post:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('정말로 이 게시글을 삭제하시겠습니까?')) {
      return;
    }

    try {
      setDeleteLoading(true);
      await postsAPI.deletePost(id);
      navigate('/posts');
    } catch (error) {
      alert('게시글 삭제에 실패했습니다.');
      console.error('Error deleting post:', error);
    } finally {
      setDeleteLoading(false);
    }
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

  if (error || !post) {
    return (
      <div className="max-w-4xl mx-auto mt-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error || '게시글을 찾을 수 없습니다.'}
        </div>
        <Link 
          to="/posts" 
          className="inline-block mt-4 text-blue-600 hover:text-blue-800"
        >
          ← 게시글 목록으로 돌아가기
        </Link>
      </div>
    );
  }

  const isAuthor = isAuthenticated && user?.id === post.user_id;

  return (
    <div className="max-w-4xl mx-auto mt-8">
      {/* 뒤로가기 링크 */}
      <Link 
        to="/posts" 
        className="inline-block mb-6 text-blue-600 hover:text-blue-800"
      >
        ← 게시글 목록으로 돌아가기
      </Link>

      {/* 게시글 내용 */}
      <article className="bg-white rounded-lg shadow-md p-8">
        {/* 헤더 */}
        <header className="border-b border-gray-200 pb-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {post.title}
          </h1>
          
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div className="flex items-center space-x-4">
              <span>작성자: {post.author.username}</span>
              <span>작성일: {formatDate(post.created_at)}</span>
              {post.updated_at !== post.created_at && (
                <span>수정일: {formatDate(post.updated_at)}</span>
              )}
            </div>
            
            {/* 작성자 전용 버튼 */}
            {isAuthor && (
              <div className="flex space-x-2">
                <Link
                  to={`/posts/${post.id}/edit`}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded text-sm"
                >
                  수정
                </Link>
                <button
                  onClick={handleDelete}
                  disabled={deleteLoading}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50"
                >
                  {deleteLoading ? '삭제 중...' : '삭제'}
                </button>
              </div>
            )}
          </div>
        </header>

        {/* 본문 */}
        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
            {post.content}
          </div>
        </div>
      </article>

      {/* AI 질의응답 섹션 (향후 구현) */}
      {isAuthenticated && (
        <div className="mt-8 bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">
            AI 어시스턴트에게 질문하기
          </h3>
          <p className="text-gray-600 mb-4">
            이 게시글과 관련된 질문을 AI에게 할 수 있습니다. (향후 구현 예정)
          </p>
          <button 
            disabled 
            className="bg-gray-400 text-white px-4 py-2 rounded cursor-not-allowed"
          >
            준비 중...
          </button>
        </div>
      )}
    </div>
  );
};

export default PostDetail;