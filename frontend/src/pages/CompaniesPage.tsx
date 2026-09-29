import React, { useEffect, useState } from 'react';
import { companiesService, CreateCompanyPayload, CreateContactPayload } from '../services/companies';
import { Company } from '../types';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { EmptyState } from '../components/ui/EmptyState';
import { getErrorMessage } from '../services/api';
import { Plus, Building2, UserPlus, Globe, Users } from 'lucide-react';

export const CompaniesPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Company Modal State
  const [isCompModalOpen, setIsCompModalOpen] = useState(false);
  const [creatingComp, setCreatingComp] = useState(false);
  const [compError, setCompError] = useState('');

  const [compName, setCompName] = useState('');
  const [industry, setIndustry] = useState('');
  const [size, setSize] = useState('');
  const [website, setWebsite] = useState('');
  const [description, setDescription] = useState('');

  // Contact Modal State
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [selectedCompId, setSelectedCompId] = useState<string | null>(null);
  const [creatingContact, setCreatingContact] = useState(false);
  const [contactError, setContactError] = useState('');

  const [contactName, setContactName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [roleInDeal, setRoleInDeal] = useState('');

  const fetchCompanies = async () => {
    try {
      setError('');
      const res = await companiesService.getCompanies();
      setCompanies(res);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const handleCreateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    setCompError('');
    setCreatingComp(true);

    try {
      const payload: CreateCompanyPayload = {
        name: compName,
        industry,
        size,
        website,
        description,
      };
      await companiesService.createCompany(payload);
      setIsCompModalOpen(false);
      setCompName('');
      setIndustry('');
      setSize('');
      setWebsite('');
      setDescription('');
      fetchCompanies();
    } catch (err) {
      setCompError(getErrorMessage(err));
    } finally {
      setCreatingComp(false);
    }
  };

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCompId) return;
    setContactError('');
    setCreatingContact(true);

    try {
      const payload: CreateContactPayload = {
        name: contactName,
        job_title: jobTitle,
        email: contactEmail,
        role_in_deal: roleInDeal,
      };
      await companiesService.addContact(selectedCompId, payload);
      setIsContactModalOpen(false);
      setContactName('');
      setJobTitle('');
      setContactEmail('');
      setRoleInDeal('');
      fetchCompanies();
    } catch (err) {
      setContactError(getErrorMessage(err));
    } finally {
      setCreatingContact(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-64" />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Companies & Contacts</h1>
          <p className="text-xs text-slate-400">Target accounts, company profiles, and key stakeholders</p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setIsCompModalOpen(true)}>
          <Plus className="w-4 h-4" />
          <span>Add Company</span>
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}

      {companies.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No companies registered"
          description="Add companies to link contacts and deals."
          actionLabel="Add Company"
          onAction={() => setIsCompModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((comp) => (
            <Card key={comp.id}>
              <CardHeader className="flex justify-between items-start">
                <div>
                  <CardTitle>{comp.name}</CardTitle>
                  {comp.industry && <p className="text-xs text-sky-400 mt-0.5">{comp.industry}</p>}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedCompId(comp.id);
                    setIsContactModalOpen(true);
                  }}
                >
                  <UserPlus className="w-3.5 h-3.5" />
                </Button>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-xs text-slate-300 line-clamp-2">{comp.description || 'No description available.'}</p>

                <div className="flex items-center gap-4 text-xs text-slate-400 pt-2 border-t border-slate-700/40">
                  {comp.size && (
                    <div className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" /> {comp.size}
                    </div>
                  )}
                  {comp.website && (
                    <div className="flex items-center gap-1 text-sky-400">
                      <Globe className="w-3.5 h-3.5" /> {comp.website}
                    </div>
                  )}
                </div>

                {/* Contacts sub-section */}
                <div className="pt-2">
                  <h5 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Contacts ({comp.contacts?.length || 0})
                  </h5>
                  {comp.contacts && comp.contacts.length > 0 ? (
                    <div className="space-y-1.5">
                      {comp.contacts.map((contact) => (
                        <div key={contact.id} className="p-2 bg-slate-900/60 rounded border border-slate-800 text-xs">
                          <p className="font-medium text-slate-200">{contact.name}</p>
                          <p className="text-[10px] text-slate-400">{contact.job_title || 'Title unassigned'} • {contact.role_in_deal || 'Stakeholder'}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No contacts added yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Company Modal */}
      <Modal isOpen={isCompModalOpen} onClose={() => setIsCompModalOpen(false)} title="Create Company Profile">
        {compError && <ErrorAlert message={compError} className="mb-4" />}

        <form onSubmit={handleCreateCompany} className="space-y-4">
          <Input
            label="Company Name"
            placeholder="Acme Corporation"
            value={compName}
            onChange={(e) => setCompName(e.target.value)}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Industry"
              placeholder="e.g. Healthcare, Software"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
            />

            <Input
              label="Company Size"
              placeholder="e.g. 500-1000 employees"
              value={size}
              onChange={(e) => setSize(e.target.value)}
            />
          </div>

          <Input
            label="Website URL"
            placeholder="https://company.com"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
          />

          <Textarea
            label="Company Description"
            placeholder="Key market details or enterprise focus..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setIsCompModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={creatingComp}>
              Create Company
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Contact Modal */}
      <Modal isOpen={isContactModalOpen} onClose={() => setIsContactModalOpen(false)} title="Add Company Contact">
        {contactError && <ErrorAlert message={contactError} className="mb-4" />}

        <form onSubmit={handleAddContact} className="space-y-4">
          <Input
            label="Contact Full Name"
            placeholder="John Doe"
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Job Title"
              placeholder="VP of Engineering"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
            />

            <Input
              label="Email Address"
              type="email"
              placeholder="john@company.com"
              value={contactEmail}
              onChange={(e) => setContactEmail(e.target.value)}
            />
          </div>

          <Input
            label="Role in Deal"
            placeholder="e.g. Economic Buyer, Champion, Technical Evaluator"
            value={roleInDeal}
            onChange={(e) => setRoleInDeal(e.target.value)}
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setIsContactModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={creatingContact}>
              Add Contact
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
