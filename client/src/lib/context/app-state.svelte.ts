import type { Mount } from '$lib/db/schema/mounts';
import type { FileSystemItem, MountIndexReport } from '$lib/mounts/mount-manager';
import type { AggregatedImage } from '$lib/api/image';
import type { ServerHealth,ModelInfo } from '$lib/api/graphcaps';

export class AppState {
    serverHealth = $state<ServerHealth | null>(null);
    serverModelInfo = $state<ModelInfo | null>(null); 
    serverApi = $state<string | null>(null);

}

export interface AppStateData {
    serverHealth: ServerHealth | null;
    serverModelInfo: ModelInfo | null;
    serverApi: string | null;
}