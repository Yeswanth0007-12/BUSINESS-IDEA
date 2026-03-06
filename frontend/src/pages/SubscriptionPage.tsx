import { useState, useEffect } from 'react';
import api from '../services/api';

interface SubscriptionPlan {
  id: number;
  name: string;
  price_monthly: number;
  max_products: number | null;
  max_boxes: number | null;
  max_optimizations_per_month: number | null;
  features: string;
}

interface UsageSummary {
  total_products: number;
  total_boxes: number;
  total_optimizations: number;
  optimizations_this_month: number;
  limit_reached: boolean;
  limit_percentage: number;
}

const SubscriptionPage = () => {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [plansData, usageData] = await Promise.all([
        api.getSubscriptionPlans(),
        api.getUsageSummary(),
      ]);
      setPlans(plansData);
      setUsage(usageData);
    } catch (error) {
      console.error('Error fetching subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const parseFeatures = (featuresStr: string) => {
    try {
      const features = JSON.parse(featuresStr);
      return Object.entries(features).map(([key, value]) => `${key}: ${value}`);
    } catch {
      return [];
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Subscription & Usage</h1>
        <p className="mt-2 text-slate-400">Manage your subscription plan and monitor usage</p>
      </div>

      {/* Usage Summary */}
      {usage && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-semibold text-slate-100 mb-4">Current Usage</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Products</div>
              <div className="text-2xl font-bold text-blue-400">{usage.total_products}</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Boxes</div>
              <div className="text-2xl font-bold text-green-400">{usage.total_boxes}</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Optimizations (This Month)</div>
              <div className="text-2xl font-bold text-purple-400">{usage.optimizations_this_month}</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-sm text-slate-400">Limit Status</div>
              <div className={`text-2xl font-bold ${usage.limit_reached ? 'text-red-400' : 'text-green-400'}`}>
                {usage.limit_percentage.toFixed(0)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Subscription Plans */}
      <div>
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className="bg-slate-800 rounded-lg border border-slate-700 p-6 hover:border-blue-500 transition-colors"
            >
              <div className="text-center">
                <h3 className="text-2xl font-bold text-slate-100 uppercase">{plan.name}</h3>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-blue-400">${plan.price_monthly}</span>
                  <span className="text-slate-400">/month</span>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <div className="flex items-center text-sm">
                  <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-slate-300">
                    {plan.max_products ? `${plan.max_products} Products` : 'Unlimited Products'}
                  </span>
                </div>
                <div className="flex items-center text-sm">
                  <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-slate-300">
                    {plan.max_boxes ? `${plan.max_boxes} Boxes` : 'Unlimited Boxes'}
                  </span>
                </div>
                <div className="flex items-center text-sm">
                  <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-slate-300">
                    {plan.max_optimizations_per_month
                      ? `${plan.max_optimizations_per_month} Optimizations/month`
                      : 'Unlimited Optimizations'}
                  </span>
                </div>
                {parseFeatures(plan.features).map((feature, idx) => (
                  <div key={idx} className="flex items-center text-sm">
                    <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-slate-300">{feature}</span>
                  </div>
                ))}
              </div>

              <button
                className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                onClick={() => alert('Upgrade functionality coming soon!')}
              >
                {plan.name === 'free' ? 'Current Plan' : 'Upgrade'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPage;
