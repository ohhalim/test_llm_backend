import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Components
import Navigation from './components/Navigation';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import PostList from './components/PostList';
import PostDetail from './components/PostDetail';
import PostForm from './components/PostForm';
import MedicalSearch from './components/MedicalSearch';

// Pages
import Home from './pages/Home';

// ProtectedRoute 컴포넌트
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router future={{ v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-gray-100">
          <Navigation />
          
          <main className="container mx-auto px-4 py-8">
            <Routes>
              {/* 공개 라우트 */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />
              <Route path="/posts" element={<PostList />} />
              <Route path="/posts/:id" element={<PostDetail />} />
              <Route path="/medical-search" element={<MedicalSearch />} />
              
              {/* 보호된 라우트 */}
              <Route 
                path="/posts/new" 
                element={
                  <ProtectedRoute>
                    <PostForm />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/posts/:id/edit" 
                element={
                  <ProtectedRoute>
                    <PostForm isEdit={true} />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;