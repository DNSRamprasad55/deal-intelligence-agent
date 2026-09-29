import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dealsService, CreateDealPayload } from '../services/deals';
import { companiesService } from '../services/companies';
import { Deal, Company, DealStage } from '../types';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Textarea } from '../components/ui/Textarea';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { EmptyState } from '../components/ui/EmptyState';
import { getErrorMessage } from '../services/api';
import { Plus, Briefcase, ChevronRight } from 'lucide-react';

export const DealsPage: React.FC = () => {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [modalError, setModalError] = useState('');

  // Form fields
  const [companyId, setCompanyId] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [stage, setStage] = useState<DealStage>('DISCOVERY');
  const [value, setValue] = useState('50000');
  const [probability, setProbability] = useState('0.20');

  const fetchData = React.useCallback(async () => {
    try {
      setError('');
      const [dealsRes, compRes] = await Promise.all([
        dealsService.getDeals(),
        companiesService.getCompanies(),
      ]);
      setDeals(dealsRes);
      setCompanies(compRes);
      if (compRes.length > 0 && !companyId) {
        setCompanyId(compRes[0].id);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyId) {
      setModalError('Please select or create a company first.');
      return;
    }
    setModalError('');
    setCreating(true);

    try {
      const payload: CreateDealPayload = {
        company_id: companyId,
        name,
        description,
        stage,
        value: parseFloat(value) || 0,
        probability: parseFloat(probability) || 0.2,
      };
      await dealsService.createDeal(payload);
      setIsModalOpen(false);
      setName('');
      setDescription('');
      fetchData();
    } catch (err) {
      setModalError(getErrorMessage(err));
    } finally {
      setCreating(false);
    }
  };

  const getStageBadgeVariant = (s: DealStage) => {
    switch (s) {
      case 'CLOSED_WON':
        return 'green';
      case 'CLOSED_LOST':
        return 'red';
      case 'NEGOTIATION':
      case 'PROPOSAL':
        return 'amber';
      default:
        return 'blue';
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-64" />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Deals Workspace</h1>
          <p className="text-xs text-slate-400">Manage pipeline deals and record interactions</p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4" />
          <span>Create Deal</span>
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}

      {deals.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No deals in workspace"
          description="Create your first deal to track stages, contacts, and historical experience."
          actionLabel="Create Deal"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-700/60 bg-slate-900/40 text-slate-400 font-medium">
                    <th className="py-3 px-4">Deal Name</th>
                    <th className="py-3 px-4">Stage</th>
                    <th className="py-3 px-4">Value</th>
                    <th className="py-3 px-4">Probability</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/40 text-slate-200">
                  {deals.map((deal) => (
                    <tr key={deal.id} className="hover:bg-slate-700/20 transition-colors">
                      <td className="py-3 px-4 font-semibold text-slate-100">
                        <Link to={`/deals/${deal.id}`} className="hover:text-sky-400">
                          {deal.name}
                        </Link>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={getStageBadgeVariant(deal.stage)}>
                          {deal.stage.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 font-mono font-medium">
                        ${Number(deal.value).toLocaleString()} {deal.currency}
                      </td>
                      <td className="py-3 px-4 font-mono">{(deal.probability * 100).toFixed(0)}%</td>
                      <td className="py-3 px-4">
                        <Badge variant={deal.status === 'OPEN' ? 'blue' : deal.status === 'WON' ? 'green' : 'red'}>
                          {deal.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          to={`/deals/${deal.id}`}
                          className="inline-flex items-center gap-1 text-sky-400 hover:text-sky-300 font-medium"
                        >
                          Workspace <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Deal Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Deal" maxWidth="lg">
        {modalError && <ErrorAlert message={modalError} className="mb-4" />}

        {companies.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-xs text-slate-400 mb-3">You need to create at least one company before adding deals.</p>
            <Link to="/companies" className="text-xs text-sky-400 hover:underline">
              Go to Companies Page to create one
            </Link>
          </div>
        ) : (
          <form onSubmit={handleCreateDeal} className="space-y-4">
            <Select
              label="Company"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              options={companies.map((c) => ({ value: c.id, label: c.name }))}
            />

            <Input
              label="Deal Name"
              placeholder="e.g. Enterprise License Expansion"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <div className="grid grid-cols-3 gap-3">
              <Select
                label="Stage"
                value={stage}
                onChange={(e) => setStage(e.target.value as DealStage)}
                options={[
                  { value: 'DISCOVERY', label: 'Discovery' },
                  { value: 'QUALIFICATION', label: 'Qualification' },
                  { value: 'TECHNICAL_EVALUATION', label: 'Technical Evaluation' },
                  { value: 'PROPOSAL', label: 'Proposal' },
                  { value: 'NEGOTIATION', label: 'Negotiation' },
                  { value: 'CLOSED_WON', label: 'Closed Won' },
                  { value: 'CLOSED_LOST', label: 'Closed Lost' },
                ]}
              />

              <Input
                label="Value (USD)"
                type="number"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                required
              />

              <Input
                label="Win Prob. (0-1)"
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={probability}
                onChange={(e) => setProbability(e.target.value)}
                required
              />
            </div>

            <Textarea
              label="Description"
              placeholder="Key objectives, scope, or background"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />

            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" isLoading={creating}>
                Create Deal
              </Button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
