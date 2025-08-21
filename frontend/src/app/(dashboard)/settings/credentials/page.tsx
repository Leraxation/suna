'use client';

import React, { useEffect } from 'react';
import { 
  Zap
} from 'lucide-react';
import { ComposioConnectionsSection } from '../../../../components/agents/composio/composio-connections-section';
import { useRouter } from 'next/navigation';
import { useFeatureFlag } from '@/lib/feature-flags';
import { PageHeader } from '@/components/ui/page-header';

export default function AppProfilesPage() {
  const { enabled: customAgentsEnabled, loading: flagLoading } = useFeatureFlag("custom_agents");
  const router = useRouter();
  
  useEffect(() => {
    if (!flagLoading && !customAgentsEnabled) {
      router.replace("/dashboard");
    }
  }, [flagLoading, customAgentsEnabled, router]);

  if (flagLoading) {
    return (
      <div className="container mx-auto max-w-7xl px-4 py-8">
        <div className="space-y-6">
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-muted rounded-3xl"></div>
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="h-32 bg-muted rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!customAgentsEnabled) {
    return null;
  }

  return (
<<<<<<< HEAD
    <div className="container mx-auto max-w-6xl px-6 py-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-foreground">MCP Credential Profiles</h1>
            </div>
          </div>
          
          <Button onClick={() => setShowAddDialog(true)} className="h-9">
            <Plus className="h-4 w-4" />
            Add Profile
          </Button>
        </div>

        <Alert className="border-primary/30 bg-primary/5">
          <Zap className="h-4 w-4 text-primary" />
          <AlertDescription className="text-sm">
            Create multiple profiles per MCP server for different use cases (teams, organizations, environments).
          </AlertDescription>
        </Alert>

        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 2 }).map((_, i) => (
              <div key={i} className="space-y-3">
                <div className="flex items-center gap-2">
                  <Skeleton className="w-8 h-8 rounded-lg"></Skeleton>
                  <div className="space-y-1">
                    <Skeleton className="h-4 w-32 rounded"></Skeleton>
                    <Skeleton className="h-3 w-24 rounded"></Skeleton>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                  {Array.from({ length: 4 }).map((_, j) => (
                    <Card key={j} className="bg-sidebar border-border/50">
                      <CardContent className="p-3">
                        <div className="animate-pulse space-y-2">
                          <div className="flex items-center gap-2">
                            <Skeleton className="w-6 h-6 rounded"></Skeleton>
                            <div className="space-y-1 flex-1">
                              <Skeleton className="h-3 w-20 rounded"></Skeleton>
                              <Skeleton className="h-2.5 w-16 rounded"></Skeleton>
                            </div>
                          </div>
                          <div className="flex gap-1">
                            <Skeleton className="h-4 w-12 rounded"></Skeleton>
                            <Skeleton className="h-4 w-8 rounded"></Skeleton>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : !profiles || profiles.length === 0 ? (
          <Card className="border-dashed border-border/60 bg-muted/20">
            <CardContent className="p-8 text-center">
              <div className="space-y-4">
                <div className="p-3 rounded-full bg-muted/60 w-fit mx-auto">
                  <Users className="h-6 w-6 text-muted-foreground" />
                </div>
                <div className="space-y-1">
                  <h3 className="font-semibold text-foreground">No profiles yet</h3>
                  <p className="text-sm text-muted-foreground">
                    Create your first credential profile to get started
                  </p>
                </div>
                <Button onClick={() => setShowAddDialog(true)} className="h-9">
                  <Plus className="h-4 w-4" />
                  Create First Profile
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedProfiles || {}).map(([qualifiedName, serverGroup]) => (
              <div key={qualifiedName} className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-primary/10">
                    <Settings2 className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground truncate">{serverGroup.serverName}</h3>
                    <p className="text-xs text-muted-foreground font-mono truncate">{serverGroup.qualifiedName}</p>
                  </div>
                  <Badge variant="outline" className="text-xs shrink-0">
                    {serverGroup.profiles.length}
                  </Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                  {serverGroup.profiles.map((profile) => (
                    <CredentialProfileCard
                      key={profile.profile_id}
                      profile={profile}
                      onDelete={handleDelete}
                      onSetDefault={handleSetDefault}
                      isDeletingId={deletingId || undefined}
                      isSettingDefaultId={settingDefaultId || undefined}
                    />
                  ))}
                </div>
                {Object.keys(groupedProfiles || {}).indexOf(qualifiedName) < Object.keys(groupedProfiles || {}).length - 1 && (
                  <Separator className="my-6" />
                )}
              </div>
            ))}
          </div>
        )}
        <EnhancedAddCredentialDialog
          open={showAddDialog}
          onOpenChange={setShowAddDialog}
          onSuccess={() => refetch()}
        />

        <DeleteConfirmationDialog
          open={showDeleteDialog}
          onOpenChange={setShowDeleteDialog}
          profileToDelete={profileToDelete}
          onConfirm={confirmDelete}
          isDeleting={!!deletingId}
        />
=======
    <div className="container mx-auto max-w-7xl px-4 py-8">
      <div className="space-y-8">
        <PageHeader icon={Zap}>
          <span className="text-primary">App Credentials</span>
        </PageHeader>
        <ComposioConnectionsSection />
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
      </div>
    </div>
  );
} 