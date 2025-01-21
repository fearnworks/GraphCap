import { API_URL, WORKSPACE } from '$lib/constants';

export const getServerHealth = async () => {
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
        api: API_URL, 
        workspace: WORKSPACE,
        serverHealth
    };
};