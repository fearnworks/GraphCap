interface ApiOptions {
	method?: string;
	body?: FormData | Record<string, unknown>;
	headers?: Record<string, string>;
}

const API_BASE = '/api/v1';

export async function api<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
	const { method = 'GET', body, headers = {} } = options;

	const response = await fetch(`${API_BASE}${endpoint}`, {
		method,
		headers: {
			...headers
		},
		body: body instanceof FormData ? body : JSON.stringify(body)
	});

	if (!response.ok) {
		throw new Error(`API error: ${response.status}`);
	}

	return response.json();
}

// Export the types
export type { ApiOptions };
