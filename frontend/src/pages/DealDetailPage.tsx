import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { dealsService } from '../services/deals';
import { interactionsService, CreateInteractionPayload } from '../services/interactions';
import { intelligenceService, DealAnalysisResponse, Recommendation, OutcomeType, OutcomeResponse } from '../services/intelligence';
import { Deal, Interaction, InteractionType } from '../types';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
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
import {
  ArrowLeft,
  Plus,
  MessageSquare,
  Clock,
  DollarSign,
  Calendar,
  Sparkles,
  BrainCircuit,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  Lightbulb,
  Check,
  X,
  Target
} from 'lucide-react';

export const DealDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [deal, setDeal] = useState<Deal | null>(null);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'intelligence' | 'interactions' | 'timeline'>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Intelligence Analysis & Reflect State
  const [analysisData, setAnalysisData] = useState<DealAnalysisResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  // Phase 5 Outcome Recording State
  const [outcomeType, setOutcomeType] = useState<OutcomeType>('POSITIVE');
  const [outcomeDescription, setOutcomeDescription] = useState('Customer accepted the phased rollout proposal and continued the deal.');
  const [outcomeImpact, setOutcomeImpact] = useState('Reduced migration concern and moved deal toward proposal.');
  const [recordingOutcome, setRecordingOutcome] = useState(false);
  const [outcomeResult, setOutcomeResult] = useState<OutcomeResponse | null>(null);
  const [outcomeError, setOutcomeError] = useState('');
  const [showOutcomeForm, setShowOutcomeForm] = useState(false);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creatingInteraction, setCreatingInteraction] = useState(false);
  const [modalError, setModalError] = useState('');

  // Form State
  const [type, setType] = useState<InteractionType>('MEETING');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const fetchDealData = useCallback(async () => {
    if (!id) return;
    try {
      setError('');
      const [dealData, interData] = await Promise.all([
        dealsService.getDealById(id),
        interactionsService.getInteractions(id),
      ]);
      setDeal(dealData);
      setInteractions(interData);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDealData();
  }, [fetchDealData]);

  const handleAnalyzeIntelligence = async () => {
    if (!id) return;
    setAnalysisError('');
    setAnalyzing(true);
    setActiveTab('intelligence');

    try {
      const res = await intelligenceService.analyzeDealIntelligence(id);
      setAnalysisData(res);
    } catch (err) {
      setAnalysisError(getErrorMessage(err));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleRecommendationAction = async (actionStatus: 'ACCEPTED' | 'REJECTED') => {
    if (!analysisData?.recommendation?.id) return;
    setActionLoading(true);

    try {
      const updatedRec: Recommendation = await intelligenceService.actOnRecommendation(
        analysisData.recommendation.id,
        actionStatus
      );
      setAnalysisData({
        ...analysisData,
        recommendation: updatedRec,
      });
      if (actionStatus === 'ACCEPTED') {
        setShowOutcomeForm(true);
      }
    } catch (err) {
      setAnalysisError(getErrorMessage(err));
    } finally {
      setActionLoading(false);
    }
  };

  const handleRecordOutcome = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!analysisData?.recommendation?.action_id) {
      setOutcomeError('No recorded action ID found for this recommendation.');
      return;
    }
    setOutcomeError('');
    setRecordingOutcome(true);

    try {
      const res = await intelligenceService.recordActionOutcome(
        analysisData.recommendation.action_id,
        {
          outcome_type: outcomeType,
          description: outcomeDescription,
          impact: outcomeImpact
        }
      );
      setOutcomeResult(res);
      setShowOutcomeForm(false);
    } catch (err) {
      setOutcomeError(getErrorMessage(err));
    } finally {
      setRecordingOutcome(false);
    }
  };

  const handleAddInteraction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    setModalError('');
    setCreatingInteraction(true);

    try {
      const payload: CreateInteractionPayload = {
        type,
        title,
        content,
      };
      await interactionsService.createInteraction(id, payload);
      setIsModalOpen(false);
      setTitle('');
      setContent('');
      fetchDealData();
    } catch (err) {
      setModalError(getErrorMessage(err));
    } finally {
      setCreatingInteraction(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-64" />;
  if (error || !deal) return <ErrorAlert message={error || 'Deal not found'} />;

  return (
    <div className="space-y-6">
      {/* Header & Navigation */}
      <div>
        <Link to="/deals" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 mb-2">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Deals
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-slate-100">{deal.name}</h1>
              <Badge variant={deal.status === 'OPEN' ? 'blue' : deal.status === 'WON' ? 'green' : 'red'}>
                {deal.status}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1">{deal.company?.name || 'Unknown Company'} • Stage: {deal.stage.replace('_', ' ')}</p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleAnalyzeIntelligence}
              isLoading={analyzing}
              className="bg-sky-600/20 text-sky-400 hover:bg-sky-600/30 border-sky-500/30"
            >
              <Sparkles className="w-4 h-4 text-sky-400" />
              <span>Analyze Deal Intelligence</span>
            </Button>

            <Button variant="primary" size="sm" onClick={() => setIsModalOpen(true)}>
              <Plus className="w-4 h-4" />
              <span>Add Interaction</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800">
        {[
          { id: 'overview', label: 'Overview' },
          { id: 'intelligence', label: `Deal Intelligence & Recommendations ${analysisData ? `(${analysisData.evidence.length})` : ''}` },
          { id: 'interactions', label: `Interactions (${interactions.length})` },
          { id: 'timeline', label: 'Timeline' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as 'overview' | 'intelligence' | 'interactions' | 'timeline')}
            className={`px-4 py-2.5 text-xs font-medium border-b-2 transition-colors cursor-pointer ${
              activeTab === tab.id
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Deal Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="text-xs font-medium text-slate-400">Description</h4>
                <p className="text-sm text-slate-200 mt-1">{deal.description || 'No description provided.'}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-700/50">
                <div>
                  <h4 className="text-xs font-medium text-slate-400">Company</h4>
                  <p className="text-sm text-slate-200 font-semibold mt-0.5">{deal.company?.name || 'N/A'}</p>
                  <p className="text-xs text-slate-400">{deal.company?.industry || 'Industry unspecified'}</p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-slate-400">Owner</h4>
                  <p className="text-sm text-slate-200 font-semibold mt-0.5">{deal.owner?.name || 'Unassigned'}</p>
                  <p className="text-xs text-slate-400">{deal.owner?.email || ''}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Deal Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
                  <DollarSign className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs text-slate-400">Deal Value</p>
                  <p className="text-base font-bold text-slate-100">${Number(deal.value).toLocaleString()} {deal.currency}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs text-slate-400">Win Probability</p>
                  <p className="text-base font-bold text-slate-100">{(deal.probability * 100).toFixed(0)}%</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-sky-500/10 text-sky-400 rounded-lg">
                  <Calendar className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs text-slate-400">Created At</p>
                  <p className="text-xs font-medium text-slate-200">{new Date(deal.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'intelligence' && (
        <div className="space-y-6">
          {analysisError && <ErrorAlert message={analysisError} />}

          {analyzing ? (
            <Card>
              <CardContent className="text-center py-12">
                <LoadingSpinner size="lg" />
                <h4 className="text-sm font-semibold text-slate-200 mt-4">Recalling historical experience and reasoning over evidence...</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                  Executing Hindsight RECALL to extract similar past deals and Hindsight REFLECT to synthesize evidence-backed next actions.
                </p>
              </CardContent>
            </Card>
          ) : analysisData?.status === 'not_configured' ? (
            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-xs">
              Connect Hindsight memory to analyze historical experiences.
            </div>
          ) : analysisData?.status === 'unavailable' ? (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
              Historical memory unavailable.
            </div>
          ) : analysisData?.status === 'no_evidence' ? (
            <EmptyState
              icon={Sparkles}
              title="No relevant historical experience found"
              description="No similar past deal memories were retrieved from Hindsight Cloud. Log additional deal details or interactions to build context."
            />
          ) : !analysisData ? (
            <EmptyState
              icon={BrainCircuit}
              title="No deal analysis generated yet"
              description="Click 'Analyze Deal Intelligence' to recall past deal experiences (WON & LOST) and run Hindsight REFLECT reasoning."
              actionLabel="Analyze Deal Intelligence"
              onAction={handleAnalyzeIntelligence}
            />
          ) : (
            <>
              {/* 1. Recommended Next Action Card */}
              {analysisData.recommendation_title && (
                <Card className="border-sky-500/40 bg-gradient-to-br from-slate-900 via-slate-900 to-sky-950/30">
                  <CardHeader className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="purple" size="sm">
                          <Sparkles className="w-3 h-3 inline mr-1" />
                          Hindsight Reflect Recommendation
                        </Badge>
                        {analysisData.recommendation?.status && (
                          <Badge
                            variant={
                              analysisData.recommendation.status === 'ACCEPTED'
                                ? 'green'
                                : analysisData.recommendation.status === 'REJECTED'
                                ? 'red'
                                : 'amber'
                            }
                            size="sm"
                          >
                            {analysisData.recommendation.status}
                          </Badge>
                        )}
                        {analysisData.recommendation?.status === 'ACCEPTED' && (
                          <Badge variant="green" size="sm">
                            <CheckCircle2 className="w-3 h-3 inline mr-1" /> Action Recorded
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-lg text-sky-300 font-bold">
                        {analysisData.recommendation_title}
                      </CardTitle>
                    </div>

                    {/* Human in the loop action buttons */}
                    {analysisData.recommendation?.id && (
                      <div className="flex items-center gap-2">
                        {analysisData.recommendation.status === 'ACCEPTED' ? (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => setShowOutcomeForm(!showOutcomeForm)}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white"
                          >
                            <Target className="w-4 h-4 mr-1" />
                            {outcomeResult ? 'Recorded Outcome' : 'Record Outcome'}
                          </Button>
                        ) : (
                          <>
                            <Button
                              variant="primary"
                              size="sm"
                              isLoading={actionLoading}
                              onClick={() => handleRecommendationAction('ACCEPTED')}
                            >
                              <Check className="w-4 h-4" /> Accept Recommendation
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              disabled={analysisData.recommendation.status === 'REJECTED'}
                              isLoading={actionLoading}
                              onClick={() => handleRecommendationAction('REJECTED')}
                            >
                              <X className="w-4 h-4 text-rose-400" /> Reject
                            </Button>
                          </>
                        )}
                      </div>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Visual Closed Learning Loop Diagram */}
                    <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                      <h6 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                        <BrainCircuit className="w-3.5 h-3.5 text-purple-400" /> Closed Learning Loop
                      </h6>
                      <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-medium">
                        <span className="px-2 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300">
                          Historical Evidence ({analysisData.evidence?.length || 0})
                        </span>
                        <span className="text-slate-600">→</span>
                        <span className="px-2 py-0.5 bg-purple-950/40 border border-purple-800/50 rounded text-purple-300">
                          AI Recommendation
                        </span>
                        <span className="text-slate-600">→</span>
                        <span className={`px-2 py-0.5 border rounded ${analysisData.recommendation?.status !== 'PENDING' ? 'bg-emerald-950/40 border-emerald-800/50 text-emerald-300' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
                          Human Decision ({analysisData.recommendation?.status || 'PENDING'})
                        </span>
                        <span className="text-slate-600">→</span>
                        <span className={`px-2 py-0.5 border rounded ${analysisData.recommendation?.status === 'ACCEPTED' ? 'bg-emerald-950/40 border-emerald-800/50 text-emerald-300' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
                          Action Recorded
                        </span>
                        <span className="text-slate-600">→</span>
                        <span className={`px-2 py-0.5 border rounded ${outcomeResult ? 'bg-emerald-950/40 border-emerald-800/50 text-emerald-300' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
                          Outcome ({outcomeResult ? outcomeResult.outcome_type : 'Pending'})
                        </span>
                        <span className="text-slate-600">→</span>
                        <span className={`px-2 py-0.5 border rounded font-semibold ${outcomeResult?.hindsight?.status === 'stored' ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300' : 'bg-slate-800 border-slate-700 text-slate-500'}`}>
                          {outcomeResult?.hindsight?.status === 'stored' ? '✓ Learned by Hindsight' : 'Hindsight Retention'}
                        </span>
                      </div>
                    </div>

                    <p className="text-sm text-slate-200">{analysisData.recommendation_description}</p>

                    {/* Why this recommendation? */}
                    <div className="p-4 bg-slate-900/90 border border-slate-700/60 rounded-xl space-y-1.5">
                      <h5 className="text-xs font-bold text-sky-400 flex items-center gap-1.5 uppercase tracking-wider">
                        <Lightbulb className="w-4 h-4" /> Why this recommendation?
                      </h5>
                      <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                        {analysisData.reasoning}
                      </p>
                    </div>

                    {/* Outcome Banners & Form */}
                    {outcomeResult && (
                      <div className="p-4 rounded-xl space-y-1 border text-xs bg-emerald-950/20 border-emerald-500/30 text-emerald-200">
                        <div className="flex items-center gap-2 font-bold text-emerald-400">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>✓ Outcome saved ({outcomeResult.outcome_type})</span>
                        </div>
                        {outcomeResult.hindsight?.status === 'stored' ? (
                          <div className="text-emerald-300 font-medium pt-1">
                            ✓ Experience retained in Hindsight memory bank ({outcomeResult.hindsight.bank_id})
                          </div>
                        ) : (
                          <div className="text-amber-400 font-medium pt-1">
                            ⚠ Outcome saved, but memory retention is currently unavailable.
                          </div>
                        )}
                        <p className="text-[11px] text-slate-300 mt-2 font-mono">
                          "{outcomeResult.description}" {outcomeResult.impact ? `• Impact: ${outcomeResult.impact}` : ''}
                        </p>
                      </div>
                    )}

                    {showOutcomeForm && !outcomeResult && (
                      <form onSubmit={handleRecordOutcome} className="p-4 bg-slate-950/90 border border-sky-500/40 rounded-xl space-y-3">
                        <h5 className="text-xs font-bold text-sky-400 flex items-center gap-1.5 uppercase tracking-wider">
                          <Target className="w-4 h-4" /> Record Outcome & Feed Memory Loop
                        </h5>

                        {outcomeError && <ErrorAlert message={outcomeError} />}

                        <Select
                          label="Outcome Result"
                          value={outcomeType}
                          onChange={(e) => setOutcomeType(e.target.value as OutcomeType)}
                          options={[
                            { value: 'POSITIVE', label: 'Positive (Outcome Succeeded)' },
                            { value: 'NEGATIVE', label: 'Negative (Outcome Failed)' },
                            { value: 'NEUTRAL', label: 'Neutral (Mixed Results)' },
                            { value: 'UNKNOWN', label: 'Unknown' },
                          ]}
                        />

                        <Textarea
                          label="Outcome Description"
                          value={outcomeDescription}
                          onChange={(e) => setOutcomeDescription(e.target.value)}
                          placeholder="Describe what actually happened after taking this action..."
                          rows={3}
                          required
                        />

                        <Input
                          label="Key Impact"
                          value={outcomeImpact}
                          onChange={(e) => setOutcomeImpact(e.target.value)}
                          placeholder="e.g. Reduced migration concern and moved deal toward proposal."
                        />

                        <div className="flex justify-end gap-2 pt-1">
                          <Button type="button" variant="ghost" size="sm" onClick={() => setShowOutcomeForm(false)}>
                            Cancel
                          </Button>
                          <Button type="submit" variant="primary" size="sm" isLoading={recordingOutcome} className="bg-emerald-600 hover:bg-emerald-500">
                            Save Outcome & Retain Memory
                          </Button>
                        </div>
                      </form>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Grid for Observed Pattern, Risks, Alternatives, Unknowns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Observed Pattern */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold flex items-center gap-2 text-slate-200">
                      <BrainCircuit className="w-4 h-4 text-purple-400" /> Observed Pattern across Past Deals
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {analysisData.observed_pattern || 'No distinct pattern observed.'}
                    </p>
                  </CardContent>
                </Card>

                {/* Identified Risks */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold flex items-center gap-2 text-amber-400">
                      <AlertTriangle className="w-4 h-4" /> Identified Risks
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysisData.risks && analysisData.risks.length > 0 ? (
                      <ul className="space-y-2 text-xs text-slate-300">
                        {analysisData.risks.map((risk, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-amber-400 font-bold">•</span>
                            <span>{risk}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No critical risks identified.</p>
                    )}
                  </CardContent>
                </Card>

                {/* Alternative Actions */}
                {analysisData.alternative_actions && analysisData.alternative_actions.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-semibold flex items-center gap-2 text-slate-200">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Alternative Actions
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-xs text-slate-300">
                        {analysisData.alternative_actions.map((alt, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-emerald-400 font-bold">•</span>
                            <span>{alt}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Unknowns */}
                {analysisData.unknowns && analysisData.unknowns.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-semibold flex items-center gap-2 text-slate-400">
                        <HelpCircle className="w-4 h-4 text-sky-400" /> Unknowns & Uncertainties
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-xs text-slate-400">
                        {analysisData.unknowns.map((unk, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-sky-400 font-bold">•</span>
                            <span>{unk}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Supporting Historical Evidence */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base font-bold text-slate-100 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-sky-400" /> Supporting Historical Evidence from Hindsight Memory
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {analysisData.evidence && analysisData.evidence.length > 0 ? (
                    <div className="space-y-4">
                      {analysisData.evidence.map((item, idx) => (
                        <div key={item.memory_id || idx} className="p-4 bg-slate-900/80 border border-slate-700/60 rounded-xl space-y-2">
                          <div className="flex justify-between items-center">
                            <div className="flex items-center gap-2">
                              <Badge variant="blue" size="sm">✓ Hindsight Memory</Badge>
                              {item.outcome_hint === 'WON' && (
                                <Badge variant="green" size="sm">
                                  <CheckCircle2 className="w-3 h-3 inline mr-1" /> WON Experience
                                </Badge>
                              )}
                              {item.outcome_hint === 'LOST' && (
                                <Badge variant="red" size="sm">
                                  <XCircle className="w-3 h-3 inline mr-1" /> LOST Experience
                                </Badge>
                              )}
                            </div>
                            {item.context && (
                              <span className="text-[10px] font-mono text-slate-500">{item.context}</span>
                            )}
                          </div>

                          <p className="text-xs text-slate-200 leading-relaxed font-sans">{item.content}</p>

                          {item.tags && item.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {item.tags.map((t, ti) => (
                                <span key={ti} className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700/40">
                                  #{t}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No supporting evidence items retrieved.</p>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}

      {activeTab === 'interactions' && (
        <Card>
          <CardHeader className="flex justify-between items-center">
            <CardTitle>Activity & Interactions</CardTitle>
            <Button variant="primary" size="sm" onClick={() => setIsModalOpen(true)}>
              <Plus className="w-4 h-4" /> Add Interaction
            </Button>
          </CardHeader>
          <CardContent>
            {interactions.length === 0 ? (
              <EmptyState
                icon={MessageSquare}
                title="No interactions recorded"
                description="Record call notes, demo feedback, or stakeholder emails to build memory."
                actionLabel="Add First Interaction"
                onAction={() => setIsModalOpen(true)}
              />
            ) : (
              <div className="space-y-4">
                {interactions.map((item) => (
                  <div key={item.id} className="p-4 bg-slate-900/60 border border-slate-700/50 rounded-xl">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2">
                        <Badge variant="purple" size="sm">
                          {item.type}
                        </Badge>
                        <h4 className="text-sm font-semibold text-slate-100">{item.title}</h4>
                      </div>
                      <span className="text-xs text-slate-400">{new Date(item.occurred_at).toLocaleString()}</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-2 whitespace-pre-wrap">{item.content}</p>
                    <div className="mt-3 pt-2 border-t border-slate-800 flex justify-between items-center text-[11px] text-slate-400">
                      <span>Memory Status:</span>
                      {item.hindsight_memory_status === 'stored' ? (
                        <Badge variant="green" size="sm">✓ Memory stored</Badge>
                      ) : item.hindsight_memory_status === 'not_configured' ? (
                        <Badge variant="amber" size="sm">⚠ Not Configured</Badge>
                      ) : item.hindsight_memory_status === 'unavailable' || item.hindsight_memory_status === 'error' ? (
                        <Badge variant="red" size="sm">⚠ Memory unavailable</Badge>
                      ) : (
                        <Badge variant="gray" size="sm">{item.hindsight_memory_status}</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'timeline' && (
        <Card>
          <CardHeader>
            <CardTitle>Deal Activity Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative pl-6 border-l border-slate-700 space-y-6">
              <div className="relative">
                <div className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-sky-500 border-2 border-slate-900" />
                <h4 className="text-xs font-semibold text-slate-200">Deal Created</h4>
                <p className="text-[11px] text-slate-400">{new Date(deal.created_at).toLocaleString()}</p>
              </div>
              {interactions.map((item) => (
                <div key={item.id} className="relative">
                  <div className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-purple-500 border-2 border-slate-900" />
                  <h4 className="text-xs font-semibold text-slate-200">{item.type}: {item.title}</h4>
                  <p className="text-[11px] text-slate-400">{new Date(item.occurred_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Interaction Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Deal Interaction">
        {modalError && <ErrorAlert message={modalError} className="mb-4" />}

        <form onSubmit={handleAddInteraction} className="space-y-4">
          <Select
            label="Interaction Type"
            value={type}
            onChange={(e) => setType(e.target.value as InteractionType)}
            options={[
              { value: 'CALL', label: 'Phone Call' },
              { value: 'MEETING', label: 'Meeting' },
              { value: 'EMAIL', label: 'Email Communication' },
              { value: 'NOTE', label: 'Internal Note' },
              { value: 'DEMO', label: 'Product Demo' },
              { value: 'TECHNICAL_REVIEW', label: 'Technical Review' },
            ]}
          />

          <Input
            label="Interaction Title"
            placeholder="e.g. Discovery Call with CTO"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />

          <Textarea
            label="Content / Notes"
            placeholder="Document key points, objections, commitments, or competitor mentions..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={5}
            required
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={creatingInteraction}>
              Save Interaction
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
