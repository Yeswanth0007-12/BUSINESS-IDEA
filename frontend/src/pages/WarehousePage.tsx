import { useState, useEffect } from 'react';
import api from '../services/api';

interface ApiKey {
  id: number;
  name: string;
  created_at: string;
  last_used_at?: string;
  is_active: boolean;
}

interface Webhook {
  id: number;
  url: string;
  events: string[];
  is_active: boolean;
  created_at: string;
}

const WarehousePage = () => {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [loading, setLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyValue, setNewKeyValue] = useState('');
  const [showNewKey, setShowNewKey] = useState(false);
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>(['optimization.completed']);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [keysData, webhooksData] = await Promise.all([
        api.listApiKeys(),
        api.listWebhooks(),
      ]);
      setApiKeys(keysData);
      setWebhooks(webhooksData);
    } catch (error) {
      console.error('Error fetching warehouse data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApiKey = async () => {
    if (!newKeyName.trim()) {
      alert('Please enter a name for the API key');
      return;
    }

    try {
      const result = await api.createApiKey(newKeyName);
      setNewKeyValue(result.api_key);
      setShowNewKey(true);
      setNewKeyName('');
      fetchData();
    } catch (error) {
      console.error('Error creating API key:', error);
      alert('Failed to create API key');
    }
  };

  const handleDeleteApiKey = async (keyId: number) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await api.deleteApiKey(keyId);
      fetchData();
    } catch (error) {
      console.error('Error deleting API key:', error);
      alert('Failed to delete API key');
    }
  };

  const handleCreateWebhook = async () => {
    if (!newWebhookUrl.trim()) {
      alert('Please enter a webhook URL');
      return;
    }

    if (!newWebhookUrl.startsWith('https://')) {
      alert('Webhook URL must use HTTPS');
      return;
    }

    if (selectedEvents.length === 0) {
      alert('Please select at least one event');
      return;
    }

    try {
      await api.registerWebhook({
        url: newWebhookUrl,
        events: selectedEvents,
        secret: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
      });
      setNewWebhookUrl('');
      setSelectedEvents(['optimization.completed']);
      fetchData();
      alert('Webhook created successfully!');
    } catch (error) {
      console.error('Error creating webhook:', error);
      alert('Failed to create webhook');
    }
  };

  const handleDeleteWebhook = async (webhookId: number) => {
    if (!confirm('Are you sure you want to delete this webhook?')) {
      return;
    }

    try {
      await api.deleteWebhook(webhookId);
      fetchData();
    } catch (error) {
      console.error('Error deleting webhook:', error);
      alert('Failed to delete webhook');
    }
  };

  const toggleEvent = (event: string) => {
    setSelectedEvents(prev => 
      prev.includes(event) 
        ? prev.filter(e => e !== event)
        : [...prev, event]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Warehouse Integration</h1>
        <p className="mt-2 text-slate-400">Manage API keys and webhooks for warehouse system integration</p>
      </div>

      {/* API Documentation Link */}
      <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
        <p className="text-sm text-blue-300">
          📚 For integration documentation, visit <span className="font-mono">/docs</span> or <span className="font-mono">/redoc</span>
        </p>
      </div>

      {/* API Keys Section */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">API Keys</h2>
        
        {/* Create New API Key */}
        <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
          <label className="block text-sm font-medium text-slate-300 mb-2">Create New API Key</label>
          <div className="flex gap-3">
            <input
              type="text"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              placeholder="API Key Name (e.g., Production WMS)"
              className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleCreateApiKey}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              Create
            </button>
          </div>
        </div>

        {/* Show New API Key */}
        {showNewKey && newKeyValue && (
          <div className="mb-6 p-4 bg-green-900/20 border border-green-700 rounded-lg">
            <p className="text-sm font-medium text-green-400 mb-2">⚠️ API Key Created - Save it now!</p>
            <p className="text-xs text-green-300 mb-3">This is the only time you'll see this key. Store it securely.</p>
            <div className="p-3 bg-slate-900 rounded font-mono text-sm text-green-400 break-all">
              {newKeyValue}
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(newKeyValue);
                alert('API key copied to clipboard!');
              }}
              className="mt-3 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Copy to Clipboard
            </button>
            <button
              onClick={() => setShowNewKey(false)}
              className="mt-3 ml-2 px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        )}

        {/* API Keys List */}
        <div className="space-y-3">
          {apiKeys.length === 0 ? (
            <p className="text-sm text-slate-400">No API keys created yet.</p>
          ) : (
            apiKeys.map((key) => (
              <div key={key.id} className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-100">{key.name}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    Created: {new Date(key.created_at).toLocaleDateString()}
                    {key.last_used_at && ` • Last used: ${new Date(key.last_used_at).toLocaleDateString()}`}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    key.is_active ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'
                  }`}>
                    {key.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <button
                    onClick={() => handleDeleteApiKey(key.id)}
                    className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Webhooks Section */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Webhooks</h2>
        
        {/* Create New Webhook */}
        <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
          <label className="block text-sm font-medium text-slate-300 mb-2">Create New Webhook</label>
          <div className="space-y-3">
            <input
              type="url"
              value={newWebhookUrl}
              onChange={(e) => setNewWebhookUrl(e.target.value)}
              placeholder="https://your-domain.com/webhook"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div>
              <label className="block text-xs text-slate-400 mb-2">Select Events:</label>
              <div className="flex gap-3">
                <label className="flex items-center gap-2 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes('optimization.completed')}
                    onChange={() => toggleEvent('optimization.completed')}
                    className="rounded"
                  />
                  optimization.completed
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes('optimization.failed')}
                    onChange={() => toggleEvent('optimization.failed')}
                    className="rounded"
                  />
                  optimization.failed
                </label>
              </div>
            </div>
            <button
              onClick={handleCreateWebhook}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              Create Webhook
            </button>
          </div>
        </div>

        {/* Webhooks List */}
        <div className="space-y-3">
          {webhooks.length === 0 ? (
            <p className="text-sm text-slate-400">No webhooks configured yet.</p>
          ) : (
            webhooks.map((webhook) => (
              <div key={webhook.id} className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-100 break-all">{webhook.url}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    Events: {webhook.events.join(', ')}
                  </p>
                  <p className="text-xs text-slate-400">
                    Created: {new Date(webhook.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    webhook.is_active ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'
                  }`}>
                    {webhook.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <button
                    onClick={() => handleDeleteWebhook(webhook.id)}
                    className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Rate Limits Info */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Rate Limits</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-slate-700/30 rounded-lg">
            <p className="text-sm text-slate-400">Standard Tier</p>
            <p className="text-2xl font-bold text-slate-100">100</p>
            <p className="text-xs text-slate-400">requests/minute</p>
          </div>
          <div className="p-4 bg-slate-700/30 rounded-lg">
            <p className="text-sm text-slate-400">Premium Tier</p>
            <p className="text-2xl font-bold text-blue-400">500</p>
            <p className="text-xs text-slate-400">requests/minute</p>
          </div>
          <div className="p-4 bg-slate-700/30 rounded-lg">
            <p className="text-sm text-slate-400">Enterprise Tier</p>
            <p className="text-2xl font-bold text-purple-400">2000</p>
            <p className="text-xs text-slate-400">requests/minute</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarehousePage;
