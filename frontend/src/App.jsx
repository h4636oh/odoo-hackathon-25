import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import LandingPage from './pages/LandingPage';
import AdminSignup from './pages/auth/AdminSignup';
import AdminSignin from './pages/auth/AdminSignin';
import UserSignin from './pages/auth/UserSignin';
import EmployeeDashboard from './pages/employee/EmployeeDashboard';
import ManagerDashboard from './pages/manager/ManagerDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUserManagement from './pages/admin/AdminUserManagement';
import Layout from './components/Layout';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user data
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/admin/signup" element={<AdminSignup onLogin={handleLogin} />} />
          <Route path="/admin/signin" element={<AdminSignin onLogin={handleLogin} />} />
          <Route path="/user/signin" element={<UserSignin onLogin={handleLogin} />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                {user.role === 'admin' ? (
                  <AdminDashboard user={user} />
                ) : (
                  <EmployeeDashboard user={user} />
                )}
              </Layout>
            ) : (
              <Navigate to="/user/signin" replace />
            )
          } />
          
          <Route path="/employee" element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <EmployeeDashboard user={user} />
              </Layout>
            ) : (
              <Navigate to="/user/signin" replace />
            )
          } />
          
          <Route path="/manager" element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <ManagerDashboard user={user} />
              </Layout>
            ) : (
              <Navigate to="/user/signin" replace />
            )
          } />
          
          <Route path="/admin" element={
            user && user.role === 'admin' ? (
              <Layout user={user} onLogout={handleLogout}>
                <AdminDashboard user={user} />
              </Layout>
            ) : (
              <Navigate to="/admin/signin" replace />
            )
          } />
          
          <Route path="/admin/users" element={
            user && user.role === 'admin' ? (
              <Layout user={user} onLogout={handleLogout}>
                <AdminUserManagement user={user} />
              </Layout>
            ) : (
              <Navigate to="/admin/signin" replace />
            )
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;