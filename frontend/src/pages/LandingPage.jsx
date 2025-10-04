import { Link } from 'react-router-dom';
import { Building2, Users, ArrowRight } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Expense Management System
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Streamline your company's expense approval process with our comprehensive management platform
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Admin Access */}
          <div className="card p-8 text-center hover:shadow-lg transition-shadow duration-200">
            <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-primary-100 mb-6">
              <Building2 className="h-8 w-8 text-primary-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Admin Access</h2>
            <p className="text-gray-600 mb-6">
              Manage your company's expense policies, create approval rules, and oversee all expense requests.
            </p>
            <div className="space-y-3">
              <Link
                to="/admin/signin"
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                Sign In as Admin
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/admin/signup"
                className="w-full btn-secondary flex items-center justify-center gap-2"
              >
                Create Company Account
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          {/* Employee/Manager Access */}
          <div className="card p-8 text-center hover:shadow-lg transition-shadow duration-200">
            <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-green-100 mb-6">
              <Users className="h-8 w-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Employee Access</h2>
            <p className="text-gray-600 mb-6">
              Submit expense requests, track their status, and manage approvals if you're a manager.
            </p>
            <Link
              to="/user/signin"
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              Sign In as Employee/Manager
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Key Features
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100 mb-4">
                <Building2 className="h-6 w-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Company Management</h4>
              <p className="text-sm text-gray-600">
                Admins can set up company accounts and manage user roles
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-green-100 mb-4">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Flexible Roles</h4>
              <p className="text-sm text-gray-600">
                Support for employees, managers, and dual-role users
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-purple-100 mb-4">
                <ArrowRight className="h-6 w-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Smart Approval</h4>
              <p className="text-sm text-gray-600">
                Customizable approval workflows and rule-based processing
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
