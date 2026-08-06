import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Plus } from "lucide-react";
import { ProjectDetail } from "@/components/projects/ProjectDetail";
import { BOQUpload } from "@/components/boqs/BOQUpload";
import { BOQVersionList } from "@/components/boqs/BOQVersionList";
import { BOQItemTable } from "@/components/boqs/BOQItemTable";
import { QuoteList } from "@/components/quotes/QuoteList";
import { QuoteBuilder } from "@/components/quotes/QuoteBuilder";
import { QuoteDetail } from "@/components/quotes/QuoteDetail";
import { DocumentReferenceList } from "@/components/documentRefs/DocumentReferenceList";
import { SustainabilityManager } from "@/pages/SustainabilityPage";

type View =
  | { tab: "overview" }
  | { tab: "boqs" }
  | { tab: "boqs-items"; boqId: string }
  | { tab: "quotes" }
  | { tab: "quotes-builder" }
  | { tab: "quotes-detail"; quoteId: string }
  | { tab: "documents" }
  | { tab: "sustainability" };

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [view, setView] = useState<View>({ tab: "overview" });

  if (!id) return null;

  const activeTab =
    view.tab.startsWith("boqs")
      ? "boqs"
      : view.tab.startsWith("quotes")
        ? "quotes"
        : view.tab === "documents"
          ? "documents"
          : view.tab === "sustainability"
            ? "sustainability"
            : "overview";

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

      <Tabs
        value={activeTab}
        onValueChange={(val) => {
          if (val === "overview") setView({ tab: "overview" });
          else if (val === "boqs") setView({ tab: "boqs" });
          else if (val === "quotes") setView({ tab: "quotes" });
          else if (val === "documents") setView({ tab: "documents" });
        }}
      >
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
              <BOQUpload projectId={id} />
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
              <Button onClick={() => setView({ tab: "quotes-builder" })}>
                <Plus className="mr-2 h-4 w-4" />
                New Quote
              </Button>
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
