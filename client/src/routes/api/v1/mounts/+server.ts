import { json } from '@sveltejs/kit';
import { mountManager } from '$lib/mounts/mount-manager';

export async function GET() {
	const mounts = await mountManager.listMounts();
	return json(mounts);
}

export async function POST({ request }) {
	const { name, path, description } = await request.json();

	try {
		const mount = await mountManager.createMount(name, path, description);
		return json(mount);
	} catch (error) {
		return json({ error: (error as Error).message }, { status: 400 });
	}
}
