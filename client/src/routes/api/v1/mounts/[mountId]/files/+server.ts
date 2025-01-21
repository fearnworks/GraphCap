import { error } from '@sveltejs/kit';
import { mountManager } from '$lib/mounts/mount-manager';
import { createReadStream } from 'fs';
import { join } from 'path';
import mime from 'mime-types';
import { listFiles } from '$lib/api/mount';

export async function GET({ params }: { params: { mountId: string } }) {
    const mountId = params.mountId as string;
    console.log(mountId);
    const result = await listFiles({ mountId, path: '' });
    return new Response(JSON.stringify(result), {
        headers: {
            'Content-Type': 'application/json'
        }
    });
}
