import type { Actions, PageServerLoad } from './$types';
import { getAllImagesWithAnnotations } from '$lib/api/image';
import type { AggregatedImage } from '$lib/api/image';
export interface DatasetLoadData {
	images: AggregatedImage[];
}

export const load: PageServerLoad<DatasetLoadData> = async () => {
	console.log('Loading images');
	const images = await getAllImagesWithAnnotations();
	console.log(images);
	return { images: images };
};

export const actions = {};
