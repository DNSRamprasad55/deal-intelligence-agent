import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dealsService } from '../services/deals';
import { DashboardMetrics } from '../types';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { EmptyState } from '../components/ui/EmptyState';
import { getErrorMessage } from '../services/api';
import { Briefcase, DollarSign, CheckCircle2, XCircle, MessageSquare, Plus } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await dealsService.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) return <LoadingSpinner size="lg" className="h-64" />;
  if (error) return <ErrorAlert message={error} />;

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
  };

  const statCards = [
    {
      title: 'Total Active Deals',
      value: metrics?.total_active_deals ?? 0,
      icon: Briefcase,
      color: 'text-sky-400',
      bg: 'bg-sky-500/10 border-sky-500/20',
    },
    {
      title: 'Open Pipeline Value',
      value: formatCurrency(metrics?.open_pipeline_value ?? 0),
      icon: DollarSign,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
    },
    {
      title: 'Won Deals',
      value: metrics?.won_deals ?? 0,
      icon: CheckCircle2,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10 border-purple-500/20',
    },
    {
      title: 'Lost Deals',
      value: metrics?.lost_deals ?? 0,
      icon: XCircle,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10 border-rose-500/20',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Deal Intelligence Dashboard</h1>
          <p className="text-xs text-slate-400">Real-time pipeline overview backed by PostgreSQL</p>
        </div>
        <Link
          to="/deals"
          className="inline-flex items-center gap-1.5 text-xs font-medium bg-sky-600 hover:bg-sky-700 text-white px-3.5 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>New Deal</span>
        </Link>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <Card key={i}>
            <CardContent className="flex items-center gap-4 p-5">
              <div className={`p-3 rounded-xl border ${stat.bg} ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-400">{stat.title}</p>
                <h3 className="text-xl font-bold text-slate-100 mt-0.5">{stat.value}</h3>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Deals & Recent Interactions Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Deals */}
        <Card>
          <CardHeader className="flex justify-between items-center">
            <CardTitle>Recent Deals</CardTitle>
            <Link to="/deals" className="text-xs text-sky-400 hover:underline">
              View All
            </Link>
          </CardHeader>
          <CardContent>
            {metrics?.recent_deals && metrics.recent_deals.length > 0 ? (
              <div className="divide-y divide-slate-700/50">
                {metrics.recent_deals.map((deal) => (
                  <Link
                    key={deal.id}
                    to={`/deals/${deal.id}`}
                    className="flex justify-between items-center py-3 first:pt-0 last:pb-0 hover:bg-slate-700/30 px-2 rounded-lg transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-200">{deal.name}</p>
                      <p className="text-xs text-slate-400">{formatCurrency(deal.value)} • Stage: {deal.stage.replace('_', ' ')}</p>
                    </div>
                    <Badge variant={deal.status === 'OPEN' ? 'blue' : deal.status === 'WON' ? 'green' : 'red'}>
                      {deal.status}
                    </Badge>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Briefcase}
                title="No deals found"
                description="Get started by creating your first deal in the workspace."
              />
            )}
          </CardContent>
        </Card>

        {/* Recent Interactions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity & Interactions</CardTitle>
          </CardHeader>
          <CardContent>
            {metrics?.recent_interactions && metrics.recent_interactions.length > 0 ? (
              <div className="space-y-3">
                {metrics.recent_interactions.map((interaction) => (
                  <div key={interaction.id} className="p-3 bg-slate-900/60 border border-slate-700/40 rounded-lg">
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="purple" size="sm">
                          {interaction.type}
                        </Badge>
                        <h4 className="text-xs font-semibold text-slate-200">{interaction.title}</h4>
                      </div>
                      <span className="text-[10px] text-slate-400">
                        {new Date(interaction.occurred_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1.5 line-clamp-2">{interaction.content}</p>
                    <div className="mt-2 text-[10px] text-slate-500 font-mono">
                      Status: {interaction.hindsight_memory_status}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={MessageSquare}
                title="No recent interactions"
                description="Log calls, meetings, or notes inside a deal to start building deal intelligence."
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
