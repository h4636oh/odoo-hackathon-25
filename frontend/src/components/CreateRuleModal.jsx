import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { X, Users, CheckCircle, UserCheck, Percent, ArrowRight } from 'lucide-react';

const CreateRuleModal = ({ request, user, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [users, setUsers] = useState([]);
  const [selectedApprovers, setSelectedApprovers] = useState([]);
  const [selectedCompulsoryApprovers, setSelectedCompulsoryApprovers] = useState([]);
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm();
  const managerRequired = watch('manager_required');
  const sequential = watch('sequential');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/admin/users', {
        headers: {
          'Authorization': `Bearer ${user.access_token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const toggleApprover = (userId) => {
    setSelectedApprovers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const toggleCompulsoryApprover = (userId) => {
    setSelectedCompulsoryApprovers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8000/admin/generate_request_rules/${request.request_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.access_token}`,
        },
        body: JSON.stringify({
          request_id: request.request_id,
          rule_description: data.rule_description,
          temp_manager: data.temp_manager || null,
          manager_required: data.manager_required === 'true',
          approvers: selectedApprovers,
          compulsory_Approvers: selectedCompulsoryApprovers,
          sequential: data.sequential === 'true',
          percentage_Required: parseFloat(data.percentage_Required) || 50
        }),
      });

      if (response.ok) {
        onSuccess();
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to create rule');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />
        
        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Create Approval Rule</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {/* Request Info */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Request Details</h4>
              <p className="text-sm text-gray-600">
                <strong>Requestor:</strong> {request.requestor} | 
                <strong> Amount:</strong> ${request.payment_Amount} | 
                <strong> Description:</strong> {request.description}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Rule Description */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rule Description *
                </label>
                <textarea
                  {...register('rule_description', { required: 'Rule description is required' })}
                  rows={3}
                  className="input-field"
                  placeholder="Describe the approval rule for this request..."
                />
                {errors.rule_description && (
                  <p className="mt-1 text-sm text-red-600">{errors.rule_description.message}</p>
                )}
              </div>

              {/* Manager Required */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Manager Required
                </label>
                <select
                  {...register('manager_required')}
                  className="input-field"
                >
                  <option value="false">No</option>
                  <option value="true">Yes</option>
                </select>
              </div>

              {/* Temporary Manager */}
              {managerRequired === 'true' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Temporary Manager
                  </label>
                  <select
                    {...register('temp_manager')}
                    className="input-field"
                  >
                    <option value="">Select manager</option>
                    {users.filter(u => u.role === 'manager').map((user) => (
                      <option key={user.user_id} value={user.user_id}>
                        {user.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Sequential Approval */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sequential Approval
                </label>
                <select
                  {...register('sequential')}
                  className="input-field"
                >
                  <option value="false">Parallel (All at once)</option>
                  <option value="true">Sequential (One after another)</option>
                </select>
              </div>

              {/* Percentage Required */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Percent className="inline h-4 w-4 mr-1" />
                  Approval Percentage Required
                </label>
                <input
                  {...register('percentage_Required', { 
                    required: 'Percentage is required',
                    min: { value: 0, message: 'Percentage must be at least 0' },
                    max: { value: 100, message: 'Percentage must be at most 100' }
                  })}
                  type="number"
                  min="0"
                  max="100"
                  className="input-field"
                  placeholder="50"
                />
                {errors.percentage_Required && (
                  <p className="mt-1 text-sm text-red-600">{errors.percentage_Required.message}</p>
                )}
              </div>
            </div>

            {/* Approvers Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="inline h-4 w-4 mr-1" />
                Select Approvers
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {users.filter(u => u.role === 'manager' || u.role === 'employee').map((user) => (
                  <div key={user.user_id} className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id={`approver-${user.user_id}`}
                      checked={selectedApprovers.includes(user.user_id)}
                      onChange={() => toggleApprover(user.user_id)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label htmlFor={`approver-${user.user_id}`} className="text-sm text-gray-900">
                      {user.name} ({user.role})
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Compulsory Approvers */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <CheckCircle className="inline h-4 w-4 mr-1" />
                Compulsory Approvers (Must approve)
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {users.filter(u => u.role === 'manager' || u.role === 'employee').map((user) => (
                  <div key={user.user_id} className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id={`compulsory-${user.user_id}`}
                      checked={selectedCompulsoryApprovers.includes(user.user_id)}
                      onChange={() => toggleCompulsoryApprover(user.user_id)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label htmlFor={`compulsory-${user.user_id}`} className="text-sm text-gray-900">
                      {user.name} ({user.role})
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Summary */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Rule Summary</h4>
              <div className="text-sm text-blue-800 space-y-1">
                <p>• {selectedApprovers.length} approver(s) selected</p>
                <p>• {selectedCompulsoryApprovers.length} compulsory approver(s)</p>
                <p>• {managerRequired === 'true' ? 'Manager approval required' : 'No manager approval required'}</p>
                <p>• {sequential === 'true' ? 'Sequential approval' : 'Parallel approval'}</p>
                <p>• {watch('percentage_Required') || 50}% approval required</p>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || selectedApprovers.length === 0}
              >
                {loading ? 'Creating Rule...' : 'Create Rule'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateRuleModal;
