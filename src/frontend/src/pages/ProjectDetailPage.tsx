import { useState, type ReactElement } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Plus } from "lucide-react";
import { ProjectDetail } from "@/components/projects/ProjectDetail";
import {
  ProjectQuickLinks,
  type ProjectTabKey,
} from "@/components/projects/ProjectQuickLinks";
import { BOQUpload } from "@/components/boqs/BOQUpload";
import { BOQVersionList } from "@/components/boqs/BOQVersionList";
import { BOQItemTable } from "@/components/boqs/BOQItemTable";
import { QuoteList } from "@/components/quotes/QuoteList";
import { QuoteBuilder } from "@/components/quotes/QuoteBuilder";
import { QuoteDetail } from "@/components/quotes/QuoteDetail";
import { DocumentReferenceList } from "@/components/documentRefs/DocumentReferenceList";
import { SustainabilityManager } from "@/pages/SustainabilityPage";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageCommercial, canWrite } from "@/lib/permissions";

type View =
  | { tab: "overview" }
  | { tab: "boqs" }
  | { tab: "boqs-items"; boqId: string }
  | { tab: "quotes" }
  | { tab: "quotes-builder" }
  | { tab: "quotes-detail"; quoteId: string }
  | { tab: "documents" }
  | { tab: "sustainability" };

export function ProjectDetailPage(): ReactElement | null {
  const { id } = useParams<{ id: string }>();
  const [view, setView] = useState<View>({ tab: "overview" });
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const commercial = canManageCommercial(user);

  const { data: project } = useQuery({
    queryKey: ["project", id],
    queryFn: () => api.getProject(id!),
    enabled: !!id,
  });

  if (!id) return null;

  const activeTab: ProjectTabKey =
    view.tab.startsWith("boqs")
      ? "boqs"
      : view.tab.startsWith("quotes")
        ? "quotes"
        : view.tab === "documents"
          ? "documents"
          : view.tab === "sustainability"
            ? "sustainability"
            : "overview";

  const handleTabChange = (val: string): void => {
    if (val === "overview") setView({ tab: "overview" });
    else if (val === "boqs") setView({ tab: "boqs" });
    else if (val === "quotes") setView({ tab: "quotes" });
    else if (val === "documents") setView({ tab: "documents" });
    else if (val === "sustainability") setView({ tab: "sustainability" });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to="/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>
      </div>

      <ProjectQuickLinks
        projectId={id}
        clientId={project?.client_id}
        activeTab={activeTab}
        onTabChange={(tab) => handleTabChange(tab)}
      />

      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="boqs">BOQs</TabsTrigger>
            <TabsTrigger value="quotes">Quotes</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="sustainability">Sustainability</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="overview">
          <ProjectDetail projectId={id} />
        </TabsContent>

        <TabsContent value="boqs">
          {view.tab === "boqs-items" ? (
            <BOQItemTable
              boqId={view.boqId}
              onBack={() => setView({ tab: "boqs" })}
            />
          ) : (
            <div className="space-y-6">
              {write ? <BOQUpload projectId={id} /> : null}
              <BOQVersionList
                projectId={id}
                onViewItems={(boqId) => setView({ tab: "boqs-items", boqId })}
              />
            </div>
          )}
        </TabsContent>

        <TabsContent value="quotes">
          {view.tab === "quotes-builder" ? (
            <QuoteBuilder
              projectId={id}
              onSuccess={() => setView({ tab: "quotes" })}
              onCancel={() => setView({ tab: "quotes" })}
            />
          ) : view.tab === "quotes-detail" ? (
            <QuoteDetail
              quoteId={view.quoteId}
              onBack={() => setView({ tab: "quotes" })}
            />
          ) : (
            <div className="space-y-6">
              {commercial ? (
                <Button onClick={() => setView({ tab: "quotes-builder" })}>
                  <Plus className="mr-2 h-4 w-4" />
                  New Quote
                </Button>
              ) : null}
              <QuoteList
                projectId={id}
                onViewQuote={(quoteId) => setView({ tab: "quotes-detail", quoteId })}
              />
            </div>
          )}
        </TabsContent>

        <TabsContent value="documents">
          <DocumentReferenceList projectId={id} />
        </TabsContent>

        <TabsContent value="sustainability">
          <SustainabilityManager projectId={id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
