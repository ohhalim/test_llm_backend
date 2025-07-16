import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { postsAPI } from '../services/api';

const PostForm = ({ isEdit = false }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [formData, setFormData] = useState({
    title: '',
    content: '',
  });
  const [loading, setLoading] = useState(false);
  const [loadingPost, setLoadingPost] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (isEdit && id) {
      fetchPost();
    }
  }, [isAuthenticated, isEdit, id, navigate]);

  const fetchPost = async () => {
    try {
      setLoadingPost(true);
      const response = await postsAPI.getPost(id);
      const post = response.data;
      
      setFormData({
        title: post.title,
        content: post.content,
      });
    } catch (error) {
      setError('게시글을 불러오는데 실패했습니다.');
      console.error('Error fetching post:', error);
    } finally {
      setLoadingPost(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isEdit) {
        await postsAPI.updatePost(id, formData);
        navigate(`/posts/${id}`);
      } else {
        const response = await postsAPI.createPost(formData);
        navigate(`/posts/${response.data.id}`);
      }
    } catch (error) {
      setError(error.response?.data?.detail || `게시글 ${isEdit ? '수정' : '작성'}에 실패했습니다.`);
    } finally {
      setLoading(false);
    }
  };

  if (loadingPost) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">게시글을 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mt-8">
      <h1 className="text-3xl font-bold mb-6">
        {isEdit ? '게시글 수정' : '새 게시글 작성'}
      </h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            제목
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="게시글 제목을 입력하세요"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
            내용
          </label>
          <textarea
            id="content"
            name="content"
            value={formData.content}
            onChange={handleChange}
            required
            rows={15}
            placeholder="게시글 내용을 입력하세요"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 resize-vertical"
          />
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate(isEdit ? `/posts/${id}` : '/posts')}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading 
              ? `${isEdit ? '수정' : '작성'} 중...` 
              : `게시글 ${isEdit ? '수정' : '작성'}`
            }
          </button>
        </div>
      </form>
    </div>
  );
};

export default PostForm;