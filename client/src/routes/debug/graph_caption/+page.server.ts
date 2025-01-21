import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/db';
import { mounts } from '$lib/db/schema/mounts';
import { getAllCaptions, getCaptionsForImage } from '$lib/api/caption';
import type { Mount } from '$lib/db/schema/mounts';
import { captionAnnotations, type CaptionAnnotation } from '$lib/db/schema/caption-annotations';

export interface DatasetLoadData {
    captions: CaptionAnnotation[];
}

export const load: PageServerLoad<DatasetLoadData> = async () => {
    console.log('Loading captions');
    const captions = await getAllCaptions();
    console.log(captions);  
    return { captions: captions };
};

export const actions = {}