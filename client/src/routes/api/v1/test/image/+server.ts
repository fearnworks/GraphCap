import { join } from "path";
import mime from "mime-types";
import { createReadStream, promises as fsPromises } from "fs";
import { error } from "@sveltejs/kit";

export async function GET({ url }) {
    console.log("v1/test/image GET");
    const fullPath = url.searchParams.get('path');

    if (!fullPath) {
        throw error(400, 'Path parameter is required');
    }

    try {
        // Verify path is within allowed directories
        const realPath = join(process.cwd(), fullPath);

        // Check if the path is a directory
        const stats = await fsPromises.stat(realPath);
        if (stats.isDirectory()) {
            const files = await fsPromises.readdir(realPath);
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
                'Cache-Control': 'public, max-age=31536000',
            },
        });
    } catch (e) {
        console.error('Error serving file:', e);
        throw error(404, 'File not found');
    }
} 