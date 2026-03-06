import { ReactNode } from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  iconColor: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const KPICard = ({ title, value, icon, iconColor, trend }: KPICardProps) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <div className={`${iconColor} p-3 rounded-lg`}>
          {icon}
        </div>
        {trend && (
          <div className={`flex items-center text-sm font-medium ${
            trend.isPositive ? 'text-green-400' : 'text-red-400'
          }`}>
            <svg
              className={`w-4 h-4 mr-1 ${trend.isPositive ? '' : 'rotate-180'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 10l7-7m0 0l7 7m-7-7v18"
              />
            </svg>
            {Math.abs(trend.value)}%
          </div>
        )}
      </div>
      <h3 className="text-slate-400 text-sm font-medium mb-1">{title}</h3>
      <p className="text-3xl font-bold text-slate-100">{value}</p>
    </div>
  );
};

export default KPICard;
