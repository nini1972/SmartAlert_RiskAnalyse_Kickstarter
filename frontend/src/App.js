import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ChartBarIcon, 
  PlusIcon, 
  CalendarIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import toast, { Toaster } from 'react-hot-toast';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [investments, setInvestments] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddProject, setShowAddProject] = useState(false);
  const [showAddInvestment, setShowAddInvestment] = useState(false);

  // Form states
  const [newProject, setNewProject] = useState({
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

  const [newInvestment, setNewInvestment] = useState({
    project_id: '',
    amount: '',
    investment_date: new Date().toISOString().split('T')[0],
    expected_return: '',
    notes: '',
    reward_tier: ''
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [projectsRes, investmentsRes, statsRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/projects`),
        axios.get(`${BACKEND_URL}/api/investments`),
        axios.get(`${BACKEND_URL}/api/dashboard/stats`)
      ]);
      
      setProjects(projectsRes.data);
      setInvestments(investmentsRes.data);
      setDashboardStats(statsRes.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard fetch error:', error);
    }
    setLoading(false);
  };

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/recommendations`);
      setRecommendations(response.data.recommendations);
    } catch (error) {
      toast.error('Failed to get AI recommendations');
    }
  };

  const handleAddProject = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const projectData = {
        ...newProject,
        goal_amount: parseFloat(newProject.goal_amount),
        pledged_amount: parseFloat(newProject.pledged_amount || 0),
        backers_count: parseInt(newProject.backers_count || 0),
        deadline: new Date(newProject.deadline).toISOString(),
        launched_date: new Date(newProject.launched_date).toISOString()
      };
      
      await axios.post(`${BACKEND_URL}/api/projects`, projectData);
      toast.success('Project added successfully!');
      setShowAddProject(false);
      setNewProject({
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
      fetchDashboardData();
    } catch (error) {
      toast.error('Failed to add project');
      console.error('Add project error:', error);
    }
    setLoading(false);
  };

  const handleAddInvestment = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const investmentData = {
        ...newInvestment,
        amount: parseFloat(newInvestment.amount),
        expected_return: newInvestment.expected_return ? parseFloat(newInvestment.expected_return) : null,
        investment_date: new Date(newInvestment.investment_date).toISOString()
      };
      
      await axios.post(`${BACKEND_URL}/api/investments`, investmentData);
      toast.success('Investment added successfully!');
      setShowAddInvestment(false);
      setNewInvestment({
        project_id: '',
        amount: '',
        investment_date: new Date().toISOString().split('T')[0],
        expected_return: '',
        notes: '',
        reward_tier: ''
      });
      fetchDashboardData();
    } catch (error) {
      toast.error('Failed to add investment');
    }
    setLoading(false);
  };

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'successful': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'live': return <ClockIcon className="h-5 w-5 text-blue-500" />;
      case 'failed': return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default: return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const riskColors = ['#10B981', '#F59E0B', '#EF4444'];
  const categoryColors = ['#3B82F6', '#8B5CF6', '#F59E0B', '#10B981', '#EF4444'];

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <ArrowTrendingUpIcon className="h-8 w-8 text-indigo-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Kickstarter Investment Tracker</h1>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowAddProject(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Project
              </button>
              <button
                onClick={() => setShowAddInvestment(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <BanknotesIcon className="h-4 w-4 mr-2" />
                Add Investment
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', name: 'Dashboard', icon: ChartBarIcon },
              { id: 'projects', name: 'Projects', icon: ClockIcon },
              { id: 'investments', name: 'Investments', icon: BanknotesIcon },
              { id: 'calendar', name: 'Calendar', icon: CalendarIcon },
              { id: 'ai-insights', name: 'AI Insights', icon: LightBulbIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'dashboard' && (
          <div className="px-4 py-6 sm:px-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Stats Cards */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ClockIcon className="h-6 w-6 text-gray-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Projects</dt>
                        <dd className="text-lg font-medium text-gray-900">{dashboardStats.total_projects || 0}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BanknotesIcon className="h-6 w-6 text-gray-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Invested</dt>
                        <dd className="text-lg font-medium text-gray-900">${(dashboardStats.total_invested || 0).toLocaleString()}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ArrowTrendingUpIcon className="h-6 w-6 text-gray-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                        <dd className="text-lg font-medium text-gray-900">{(dashboardStats.success_rate || 0).toFixed(1)}%</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BanknotesIcon className="h-6 w-6 text-gray-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Avg Investment</dt>
                        <dd className="text-lg font-medium text-gray-900">${(dashboardStats.avg_investment || 0).toLocaleString()}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Risk Distribution */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Risk Distribution</h3>
                  <div className="mt-5">
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={dashboardStats.risk_distribution || []}
                          dataKey="count"
                          nameKey="_id"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                        >
                          {(dashboardStats.risk_distribution || []).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={riskColors[index % riskColors.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Category Distribution */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Category Distribution</h3>
                  <div className="mt-5">
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={dashboardStats.category_distribution || []}
                          dataKey="count"
                          nameKey="_id"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                        >
                          {(dashboardStats.category_distribution || []).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={categoryColors[index % categoryColors.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'projects' && (
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Your Projects</h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">Track all your Kickstarter investments</p>
              </div>
              <ul className="divide-y divide-gray-200">
                {projects.map((project) => (
                  <li key={project.id} className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        {getStatusIcon(project.status)}
                        <div className="ml-4">
                          <div className="flex items-center">
                            <p className="text-sm font-medium text-indigo-600 truncate">{project.name}</p>
                            <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(project.risk_level)}`}>
                              {project.risk_level} risk
                            </span>
                          </div>
                          <p className="text-sm text-gray-500">by {project.creator} • {project.category}</p>
                          <p className="text-sm text-gray-500">
                            ${project.pledged_amount?.toLocaleString()} of ${project.goal_amount?.toLocaleString()} 
                            • {project.backers_count} backers
                          </p>
                        </div>
                      </div>
                      <div className="flex flex-col items-end">
                        <p className="text-sm text-gray-500">Deadline</p>
                        <p className="text-sm font-medium text-gray-900">
                          {format(new Date(project.deadline), 'MMM dd, yyyy')}
                        </p>
                      </div>
                    </div>
                    {project.ai_analysis && (
                      <div className="mt-3 bg-gray-50 rounded-lg p-3">
                        <p className="text-xs text-gray-600">
                          AI Analysis: Success probability {(project.ai_analysis.success_probability * 100).toFixed(0)}%
                          • Sentiment score {(project.ai_analysis.sentiment_score * 100).toFixed(0)}%
                        </p>
                      </div>
                    )}
                  </li>
                ))}
                {projects.length === 0 && (
                  <li className="px-4 py-12 text-center">
                    <p className="text-gray-500">No projects yet. Add your first project to get started!</p>
                  </li>
                )}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'investments' && (
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Your Investments</h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">Track your financial commitments</p>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expected Return</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {investments.map((investment) => {
                      const project = projects.find(p => p.id === investment.project_id);
                      return (
                        <tr key={investment.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{project?.name || 'Unknown Project'}</div>
                            <div className="text-sm text-gray-500">{investment.reward_tier}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">${investment.amount?.toLocaleString()}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">
                              {format(new Date(investment.investment_date), 'MMM dd, yyyy')}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">
                              {investment.expected_return ? `$${investment.expected_return.toLocaleString()}` : 'N/A'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{investment.notes || 'N/A'}</div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {investments.length === 0 && (
                  <div className="px-6 py-12 text-center">
                    <p className="text-gray-500">No investments yet. Add your first investment to get started!</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ai-insights' && (
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">AI-Powered Insights</h3>
                  <button
                    onClick={fetchRecommendations}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    <LightBulbIcon className="h-4 w-4 mr-2" />
                    Get New Recommendations
                  </button>
                </div>
                
                {recommendations.length > 0 ? (
                  <div className="space-y-4">
                    {recommendations.map((rec, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-800">{rec}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <LightBulbIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No recommendations yet</h3>
                    <p className="mt-1 text-sm text-gray-500">Click the button above to get AI-powered investment insights.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'calendar' && (
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Project Timeline</h3>
                <div className="mt-6 space-y-4">
                  {projects
                    .filter(p => p.status === 'live')
                    .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))
                    .map((project) => (
                      <div key={project.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{project.name}</h4>
                          <p className="text-sm text-gray-500">by {project.creator}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-900">
                            {format(new Date(project.deadline), 'MMM dd, yyyy')}
                          </p>
                          <p className="text-sm text-gray-500">
                            {Math.max(0, Math.ceil((new Date(project.deadline) - new Date()) / (1000 * 60 * 60 * 24)))} days remaining
                          </p>
                        </div>
                      </div>
                    ))}
                  {projects.filter(p => p.status === 'live').length === 0 && (
                    <p className="text-center text-gray-500 py-8">No active projects with upcoming deadlines.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Add Project Modal */}
      {showAddProject && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Project</h3>
              <form onSubmit={handleAddProject} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Project Name</label>
                    <input
                      type="text"
                      required
                      value={newProject.name}
                      onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Creator</label>
                    <input
                      type="text"
                      required
                      value={newProject.creator}
                      onChange={(e) => setNewProject({...newProject, creator: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Kickstarter URL</label>
                  <input
                    type="url"
                    required
                    value={newProject.url}
                    onChange={(e) => setNewProject({...newProject, url: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    required
                    value={newProject.description}
                    onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                    rows={3}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Category</label>
                    <select
                      value={newProject.category}
                      onChange={(e) => setNewProject({...newProject, category: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="Technology">Technology</option>
                      <option value="Design">Design</option>
                      <option value="Games">Games</option>
                      <option value="Film">Film</option>
                      <option value="Music">Music</option>
                      <option value="Arts">Arts</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Goal Amount ($)</label>
                    <input
                      type="number"
                      required
                      value={newProject.goal_amount}
                      onChange={(e) => setNewProject({...newProject, goal_amount: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Current Pledged ($)</label>
                    <input
                      type="number"
                      value={newProject.pledged_amount}
                      onChange={(e) => setNewProject({...newProject, pledged_amount: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Launch Date</label>
                    <input
                      type="date"
                      required
                      value={newProject.launched_date}
                      onChange={(e) => setNewProject({...newProject, launched_date: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Deadline</label>
                    <input
                      type="date"
                      required
                      value={newProject.deadline}
                      onChange={(e) => setNewProject({...newProject, deadline: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAddProject(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                  >
                    {loading ? 'Adding...' : 'Add Project'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add Investment Modal */}
      {showAddInvestment && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Investment</h3>
              <form onSubmit={handleAddInvestment} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Project</label>
                  <select
                    required
                    value={newInvestment.project_id}
                    onChange={(e) => setNewInvestment({...newInvestment, project_id: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select a project</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>{project.name}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Investment Amount ($)</label>
                    <input
                      type="number"
                      required
                      value={newInvestment.amount}
                      onChange={(e) => setNewInvestment({...newInvestment, amount: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Investment Date</label>
                    <input
                      type="date"
                      required
                      value={newInvestment.investment_date}
                      onChange={(e) => setNewInvestment({...newInvestment, investment_date: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Expected Return ($)</label>
                    <input
                      type="number"
                      value={newInvestment.expected_return}
                      onChange={(e) => setNewInvestment({...newInvestment, expected_return: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Reward Tier</label>
                    <input
                      type="text"
                      value={newInvestment.reward_tier}
                      onChange={(e) => setNewInvestment({...newInvestment, reward_tier: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Notes</label>
                  <textarea
                    value={newInvestment.notes}
                    onChange={(e) => setNewInvestment({...newInvestment, notes: e.target.value})}
                    rows={3}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAddInvestment(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                  >
                    {loading ? 'Adding...' : 'Add Investment'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;