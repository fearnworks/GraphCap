import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/db';
import { mounts } from '$lib/db/schema/mounts';
import type { Mount } from '$lib/db/schema/mounts';
import { generateCaptions } from '$lib/api/joycap';

export interface DatasetLoadData {
	mounts: Mount[];
}

export const load: PageServerLoad<DatasetLoadData> = async () => {
	const mountPoints = await db.select().from(mounts);
	console.log(mountPoints);
	return { mounts: mountPoints };
};

export const actions: Actions = {
	generateCaptions: async ({ request }) => {
		// const formData = await request.formData();
		// const mountId = formData.get('mountId') as string;
		const mountId = '1';
		// console.log('Server Generate Captions', { mountId });
		return await generateCaptions(mountId);
	}
};
