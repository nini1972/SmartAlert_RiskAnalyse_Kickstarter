import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useAppContext } from '../../context/AppContext';

const AddProjectModal = ({ isOpen, onClose }) => {
  const { addProject, loading } = useAppContext();

  const [formData, setFormData] = useState({
    name: '',
    creator: '',
    url: '',
    description: '',
    category: 'Technology',
    goal_amount: '',
    pledged_amount: '',
    backers_count: '',
    deadline: '',
    launched_date: '',
    status: 'live'
  });

  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) newErrors.name = 'Project name is required';
    if (!formData.creator.trim()) newErrors.creator = 'Creator name is required';
    if (!formData.url.trim()) newErrors.url = 'URL is required';
    if (!formData.url.match(/^https?:\/\//)) newErrors.url = 'URL must start with http:// or https://';
    if (!formData.description.trim()) newErrors.description = 'Description is required';
    if (formData.description.length < 10) newErrors.description = 'Description must be at least 10 characters';
    if (!formData.goal_amount || parseFloat(formData.goal_amount) <= 0) newErrors.goal_amount = 'Valid goal amount is required';
    if (!formData.deadline) newErrors.deadline = 'Deadline is required';
    if (!formData.launched_date) newErrors.launched_date = 'Launch date is required';
    
    if (formData.deadline && formData.launched_date) {
      if (new Date(formData.deadline) <= new Date(formData.launched_date)) {
        newErrors.deadline = 'Deadline must be after launch date';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      const projectData = {
        ...formData,
        goal_amount: parseFloat(formData.goal_amount),
        pledged_amount: parseFloat(formData.pledged_amount || 0),
        backers_count: parseInt(formData.backers_count || 0),
        deadline: new Date(formData.deadline).toISOString(),
        launched_date: new Date(formData.launched_date).toISOString()
      };
      
      await addProject(projectData);
      handleClose();
    } catch (error) {
      console.error('Failed to add project:', error);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      creator: '',
      url: '',
      description: '',
      category: 'Technology',
      goal_amount: '',
      pledged_amount: '',
      backers_count: '',
      deadline: '',
      launched_date: '',
      status: 'live'
    });
    setErrors({});
    onClose();
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
      <div className="relative p-5 border w-11/12 md:w-3/4 lg:w-1/2 max-w-4xl shadow-lg rounded-md bg-white max-h-90vh overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Add New Kickstarter Project</h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close modal"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">Project Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                  errors.name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter project name"
              />
              {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
            </div>
            
            <div>
              <label htmlFor="creator" className="block text-sm font-medium text-gray-700">Creator *</label>
              <input
                type="text"
                id="creator"
                name="creator"
                required
                value={formData.creator}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                  errors.creator ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Creator or company name"
              />
              {errors.creator && <p className="mt-1 text-sm text-red-600">{errors.creator}</p>}
            </div>
          </div>

          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700">Kickstarter URL *</label>
            <input
              type="url"
              id="url"
              name="url"
              required
              value={formData.url}
              onChange={handleInputChange}
              className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                errors.url ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="https://www.kickstarter.com/projects/..."
            />
            {errors.url && <p className="mt-1 text-sm text-red-600">{errors.url}</p>}
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description *</label>
            <textarea
              id="description"
              name="description"
              required
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                errors.description ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Describe the project..."
            />
            {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
            <p className="mt-1 text-sm text-gray-500">{formData.description.length}/2000 characters</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">Category</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="Technology">Technology</option>
                <option value="Design">Design</option>
                <option value="Games">Games</option>
                <option value="Film">Film</option>
                <option value="Music">Music</option>
                <option value="Arts">Arts</option>
                <option value="Food">Food</option>
                <option value="Fashion">Fashion</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="goal_amount" className="block text-sm font-medium text-gray-700">Goal Amount ($) *</label>
              <input
                type="number"
                id="goal_amount"
                name="goal_amount"
                required
                min="1"
                step="0.01"
                value={formData.goal_amount}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                  errors.goal_amount ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="10000"
              />
              {errors.goal_amount && <p className="mt-1 text-sm text-red-600">{errors.goal_amount}</p>}
            </div>
            
            <div>
              <label htmlFor="pledged_amount" className="block text-sm font-medium text-gray-700">Current Pledged ($)</label>
              <input
                type="number"
                id="pledged_amount"
                name="pledged_amount"
                min="0"
                step="0.01"
                value={formData.pledged_amount}
                onChange={handleInputChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="0"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="backers_count" className="block text-sm font-medium text-gray-700">Backers Count</label>
              <input
                type="number"
                id="backers_count"
                name="backers_count"
                min="0"
                value={formData.backers_count}
                onChange={handleInputChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="0"
              />
            </div>
            
            <div>
              <label htmlFor="launched_date" className="block text-sm font-medium text-gray-700">Launch Date *</label>
              <input
                type="date"
                id="launched_date"
                name="launched_date"
                required
                value={formData.launched_date}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                  errors.launched_date ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.launched_date && <p className="mt-1 text-sm text-red-600">{errors.launched_date}</p>}
            </div>
            
            <div>
              <label htmlFor="deadline" className="block text-sm font-medium text-gray-700">Deadline *</label>
              <input
                type="date"
                id="deadline"
                name="deadline"
                required
                value={formData.deadline}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                  errors.deadline ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.deadline && <p className="mt-1 text-sm text-red-600">{errors.deadline}</p>}
            </div>
          </div>

          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="live">Live</option>
              <option value="successful">Successful</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading.projects}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading.projects ? 'Adding...' : 'Add Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddProjectModal;