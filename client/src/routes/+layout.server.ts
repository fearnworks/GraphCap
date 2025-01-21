import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/db';
import { mounts } from '$lib/db/schema/mounts';
import type { Mount } from '$lib/db/schema/mounts';
import type { ModelInfo, ServerHealth } from '$lib/api/graphcaps';
import { API_URL, WORKSPACE } from '$lib/constants';

export interface LayoutLoadData {
    serverHealth: ServerHealth;
    serverModelInfo: ModelInfo;
    serverApi: string;
}

export const load: PageServerLoad = async () => {
    // Fetch server health
    let serverHealth = { status: 'unknown', modelInfo: null, error: null };
    
    try {
        const [healthResponse, modelInfoResponse] = await Promise.all([
            fetch(`${API_URL}/server/health`),
            fetch(`${API_URL}/server/model_info`)
        ]);

        if (healthResponse.ok && modelInfoResponse.ok) {
            const health = await healthResponse.json();
            const modelInfo = await modelInfoResponse.json();
            serverHealth = {
                status: health.status,
                modelInfo,
                error: null
            };
        }
    } catch (error) {
        console.error('Error fetching server health:', error);
    }

    return { 
        serverApi: API_URL, 
        serverWorkspace: WORKSPACE,
        serverHealth: serverHealth
    };
};