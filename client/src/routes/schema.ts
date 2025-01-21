import { z } from 'zod';

export const schema = z.object({
	images: z
		.instanceof(File, { message: 'Please upload a file.' })
		.refine((f) => f.size < 100_000_000, 'Max 100MB upload size.')
		.array(),
	image: z
		.instanceof(File, { message: 'Please upload a file.' })
		.refine((f) => f.size < 100_000_000, 'Max 100MB upload size.')
});
