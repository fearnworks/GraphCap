import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/db';
import { mounts } from '$lib/db/schema/mounts';
import { generateCaption, queueCaptionsForMount } from '$lib/api/caption';
import { createMount, listFiles, indexUnindexedFiles } from '$lib/api/mount';
import type { Mount } from '$lib/db/schema/mounts';
import { generateReasoning } from '$lib/api/chain_of_thought';

export interface DatasetLoadData {
    mounts: Mount[];
}

export const load: PageServerLoad<DatasetLoadData> = async () => {
    const mountPoints = await db.select().from(mounts);
    console.log(mountPoints);
    return { mounts: mountPoints };
};

export const actions = {
    createMount: async ({ request }) => {
        const formData = await request.formData();
        const name = formData.get('name') as string;
        const path = formData.get('path') as string;
        const description = formData.get('description') as string;

        return await createMount({ name, path, description });
    },

    generateCaption: async ({ request }) => {
        const formData = await request.formData();
        const imageId = formData.get('imageId') as string;
        const mountId = formData.get('mountId') as string;
        console.log('Server Generate Caption', imageId, mountId);
        return await generateCaption({ imageId, mountId });
    },

    listFiles: async ({ request }) => {
        const formData = await request.formData();
        const mountId = formData.get('mountId') as string;
        const path = formData.get('path') as string || '';
        return await listFiles({ mountId, path });
    },

    indexFiles: async ({ request }) => {
        const formData = await request.formData();
        const mountId = formData.get('mountId') as string;
        const path = formData.get('path') as string || '';
        
        return await indexUnindexedFiles({ mountId, path });
    },

    queueCaptions: async ({ request }) => {
        const formData = await request.formData();
        const mountId = formData.get('mountId') as string;
        return await queueCaptionsForMount(mountId);
    },

    generateReasoning: async ({ request }) => {
        const formData = await request.formData();
        const imageId = formData.get('imageId') as string;
        const mountId = formData.get('mountId') as string;
        const question = formData.get('question') as string;
        
        console.log('Server Generate Reasoning', { imageId, mountId, question });
        return await generateReasoning({ imageId, mountId, question });
    },
};
