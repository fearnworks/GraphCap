import { mountManager } from '$lib/mounts/mount-manager';
import { join } from 'path';
import mime from 'mime-types';
import { createReadStream } from 'fs';
import { error } from '@sveltejs/kit';

export async function GET({ params, url }) {
	console.log('v1/mounts/[mountId]/image GET');
	const { mountId } = params;
	const path = url.searchParams.get('path') || '';

	try {
		const mount = await mountManager.getMount(mountId);
		const fullPath = join(mount.path, path);

		// Verify path is within mount directory
		const realPath = await mountManager.verifyPathSafety(mountId, path);

		// If no path or directory, list files
		if (!path || (await mountManager.isDirectory(realPath))) {
			const files = await mountManager.listFiles(mountId, path);
			return new Response(JSON.stringify(files), {
				headers: { 'Content-Type': 'application/json' }
			});
		}

		// Serve the file
		const mimeType = mime.lookup(fullPath) || 'application/octet-stream';
		const fileStream = createReadStream(realPath);

		return new Response(fileStream as any, {
			headers: {
				'Content-Type': mimeType,
				'Cache-Control': 'public, max-age=31536000'
			}
		});
	} catch (e) {
		console.error('Error serving file:', e);
		throw error(404, 'File not found');
	}
}
