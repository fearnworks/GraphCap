import type { Mount } from '$lib/db/schema/mounts';
import type { FileSystemItem, MountIndexReport } from '$lib/mounts/mount-manager';
import type { AggregatedImage } from '$lib/api/image';

export class DatasetState {
    mounts = $state<Mount[]>([]);
    selectedMount = $state<Mount | null>(null);
    mountFiles = $state<MountIndexReport | null>(null);
    selectedImage = $state<AggregatedImage | null>(null);

    constructor() {
        $effect(() => {
            // Clear dependent states when selectedMount changes
            if (this.selectedMount) {
                this.mountFiles = null;
                this.selectedImage = null;
            }
        });
    }
}