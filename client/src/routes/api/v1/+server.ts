import { json } from '@sveltejs/kit';
import { API_URL } from '$lib/constants';



// Get server health status
export async function GET({ url }: { url: URL }) {
    const action = url.searchParams.get('action');
    console.log(`v1 GET: ${action}`);
    try {
        switch (action) {
            case 'health':
                const response = await fetch(`${API_URL}/server/health`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return json(data);

            case 'model_info':
                const modelResponse = await fetch(`${API_URL}/server/model_info`);
                if (!modelResponse.ok) {
                    throw new Error(`HTTP error! status: ${modelResponse.status}`);
                }
                const modelData = await modelResponse.json();
                return json(modelData);

            case 'schemas':
                const schemasResponse = await fetch(`${API_URL}/server/schemas`);
                if (!schemasResponse.ok) {
                    throw new Error(`HTTP error! status: ${schemasResponse.status}`);
                }
                const schemasData = await schemasResponse.json();
                return json(schemasData);

            default:
                return json({ error: 'Invalid action' }, { status: 400 });
        }
    } catch (error) {
        console.error('Error fetching GraphCap server info:', error);
        return json({ error: 'Failed to fetch server information' }, { status: 500 });
    }
}
