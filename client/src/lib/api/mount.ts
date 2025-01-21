import { db } from '$lib/db';
import { mounts } from '$lib/db/schema/mounts';
import { imageInfo } from '$lib/db/schema/image-info';
import { eq, and } from 'drizzle-orm';
import { join } from 'node:path';
import { existsSync, readdirSync } from 'node:fs';
import { ImageIndexer } from '$lib/mounts/image-indexer';

export const createMount = async ({ name, path, description}: { name: string, path: string, description: string }) => {

    try {
        const newMount = await db.insert(mounts).values({
            name,
            path,
            description,
            type: 'local'
        }).returning();
        
        return { success: true, mount: newMount[0] };
    } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        return { success: false, error: errorMessage };
    }
}

export const listFiles = async ({ mountId, path }: { mountId: string, path: string }) => {
    try {
        const [mount] = await db
            .select()
            .from(mounts)
            .where(eq(mounts.id, mountId));

        if (!mount) throw new Error('Mount not found');

        const fullPath = join(mount.path, path);
        if (!existsSync(fullPath)) throw new Error('Path does not exist');
        console.log(`[listFiles] Searching for indexed images for`);
        // Get indexed images from the database for this path
        const indexedImages = await db.query.imageInfo.findMany({
            where: and(
                eq(imageInfo.mountId, mountId),
            )
        });
        console.log(`[listFiles] Found ${indexedImages.length} indexed images`);

        // Create a Set of indexed filenames for quick lookup
        const indexedFilenames = new Set(indexedImages.map(img => img.relativePath.split('/').pop()));

        // Get all files in the directory
        const dirEntries = readdirSync(fullPath, { withFileTypes: true });
        
        const [indexedFiles, unindexedFiles] = dirEntries.reduce((acc, dirent) => {
            const [indexed, unindexed] = acc;
            const isIndexed = indexedFilenames.has(dirent.name);
            const indexedData = isIndexed 
                ? indexedImages.find(img => img.relativePath.split('/').pop() === dirent.name)
                : null;

            const fileInfo = {
                name: dirent.name,
                isDirectory: dirent.isDirectory(),
                path: join(path, dirent.name),
                ...(indexedData && {
                    imageId: indexedData.id,
                    width: indexedData.width,
                    height: indexedData.height,
                    fileSize: indexedData.fileSize,
                    mimeType: indexedData.mimeType
                })
            };

            if (isIndexed && indexedData) {
                indexed.push(fileInfo);
            } else {
                unindexed.push(fileInfo);
            }

            return [indexed, unindexed];
        }, [[], []] as [any[], any[]]);

        return { 
            success: true, 
            indexedFiles,
            unindexedFiles,
            directories: dirEntries
                .filter(dirent => dirent.isDirectory())
                .map(dirent => ({
                    name: dirent.name,
                    path: join(path, dirent.name),
                    isDirectory: true
                })),
            stats: {
                total: dirEntries.length,
                indexed: indexedFiles.length,
                unindexed: unindexedFiles.length,
                directories: dirEntries.filter(d => d.isDirectory()).length
            }
        };
    } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        return { success: false, error: errorMessage };
    }
}

export const indexUnindexedFiles = async ({ mountId, path }: { mountId: string, path: string }) => {
    console.log(`[indexUnindexedFiles] Starting indexing for mount ${mountId} at path: ${path}`);
    
    try {
        // Get mount information
        const [mount] = await db
            .select()
            .from(mounts)
            .where(eq(mounts.id, mountId));

        if (!mount) {
            console.error(`[indexUnindexedFiles] Mount not found: ${mountId}`);
            throw new Error('Mount not found');
        }

        console.log(`[indexUnindexedFiles] Found mount: ${mount.name}`);

        const indexer = new ImageIndexer(mount);
        try {
            // Pass the relative path to indexDirectory
            await indexer.indexDirectory(mount.path);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        }

       
    } catch (error) {
        console.error('[indexUnindexedFiles] Fatal error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        return { 
            success: false, 
            error: errorMessage,
            results: null
        };
    }
};

// Add a method to get indexing status
export const getIndexingStatus = async ({ mountId, path }: { mountId: string, path: string }) => {
    console.log(`[getIndexingStatus] Checking status for mount ${mountId} at path: ${path}`);
    
    try {
        const indexedFiles = await db.query.imageInfo.findMany({
            where: and(
                eq(imageInfo.mountId, mountId),
                eq(imageInfo.relativePath, path)
            )
        });

        const fullPath = join((await db.query.mounts.findFirst({
            where: eq(mounts.id, mountId)
        }))!.path, path);

        const allFiles = readdirSync(fullPath, { withFileTypes: true })
            .filter(entry => !entry.isDirectory());

        const status = {
            total: allFiles.length,
            indexed: indexedFiles.length,
            unindexed: allFiles.length - indexedFiles.length,
            completionRate: `${((indexedFiles.length / allFiles.length) * 100).toFixed(1)}%`
        };

        console.log('[getIndexingStatus] Status:', status);
        return { success: true, status };
    } catch (error) {
        console.error('[getIndexingStatus] Error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        return { success: false, error: errorMessage };
    }
};