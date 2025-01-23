import { existsSync, readdirSync, statSync } from 'fs';
import { resolve, join } from 'path';
import { db } from '$lib/db';
import { mounts, imageInfo } from '$lib/db/schema';
import { eq, and } from 'drizzle-orm';
import { promises as fs } from 'fs';
import { ImageIndexer } from './image-indexer';

export interface FileSystemItem {
	name: string;
	isDirectory: boolean;
	path: string;
	size: number;
	modified: Date;
	imageId?: string;
}

export interface MountIndexReport {
	indexedFiles: Array<{
		name: string;
		path: string;
		isDirectory: boolean;
		imageId?: string;
		width?: number;
		height?: number;
		fileSize?: number;
		mimeType?: string;
	}>;
	unindexedFiles: Array<{
		name: string;
		path: string;
		isDirectory: boolean;
	}>;
	directories: Array<{
		name: string;
		path: string;
		isDirectory: boolean;
	}>;
	stats: {
		total: number;
		indexed: number;
		unindexed: number;
		directories: number;
	};
}

export class MountManager {
	async createMount(name: string, path: string, description?: string) {
		const absolutePath = resolve(path);

		if (!existsSync(absolutePath)) {
			throw new Error(`Path does not exist: ${absolutePath}`);
		}

		const [mount] = await db
			.insert(mounts)
			.values({
				name,
				path: absolutePath,
				description,
				type: 'local'
			})
			.returning();

		return mount;
	}

	async listMounts() {
		return await db.select().from(mounts);
	}

	async getMount(id: string) {
		const [mount] = await db.select().from(mounts).where(eq(mounts.id, id));
		if (!mount) {
			throw new Error(`Mount not found: ${id}`);
		}
		return mount;
	}

	private async getIndexedFiles(mountId: string) {
		/* @doc
		 * Get all indexed files for a mount based on mountId
		 */
		const files = await db
			.select()
			.from(imageInfo)
			.where(and(eq(imageInfo.mountId, mountId)));
		console.log('[getIndexedFiles] Found indexed files:', files.length);
		return files;
	}

	private async readFileSystem(fullPath: string, subPath: string): Promise<FileSystemItem[]> {
		console.log('[readFileSystem] Reading directory:', fullPath);
		try {
			const items = readdirSync(fullPath, { withFileTypes: true })
				.map((dirent) => {
					const filePath = join(subPath, dirent.name);
					const fullFilePath = join(fullPath, dirent.name);

					try {
						const stats = statSync(fullFilePath);
						return {
							name: dirent.name,
							isDirectory: stats.isDirectory(),
							path: filePath,
							size: stats.size,
							modified: stats.mtime
						};
					} catch (e) {
						console.warn(`[readFileSystem] Skipping inaccessible file: ${dirent.name}`, e);
						return null;
					}
				})
				.filter((item): item is NonNullable<typeof item> => item !== null);

			console.log('[readFileSystem] Found items:', items.length);
			return items;
		} catch (error) {
			console.error('[readFileSystem] Error reading directory:', error);
			throw error;
		}
	}

	private categorizeFiles(
		allFiles: FileSystemItem[],
		indexedFiles: (typeof imageInfo.$inferSelect)[]
	): Pick<MountIndexReport, 'indexedFiles' | 'unindexedFiles' | 'directories'> {
		console.log('[categorizeFiles] Categorizing files...');

		// Create indexed files map for faster lookup
		const indexedFilesMap = new Map(indexedFiles.map((file) => [file.relativePath, file]));

		// Separate directories
		const directories = allFiles
			.filter((f) => f.isDirectory)
			.map((dir) => ({
				name: dir.name,
				path: dir.path,
				isDirectory: true
			}));

		// Process regular files
		const { indexed, unindexed } = allFiles
			.filter((f) => !f.isDirectory)
			.reduce(
				(acc, file) => {
					const indexedFile = indexedFilesMap.get(file.name);

					if (indexedFile) {
						acc.indexed.push({
							...file,
							imageId: indexedFile.id,
							width: indexedFile.width,
							height: indexedFile.height,
							fileSize: indexedFile.fileSize,
							mimeType: indexedFile.mimeType
						});
					} else if (this.isImageFile(file.name)) {
						acc.unindexed.push(file);
					}
					return acc;
				},
				{
					indexed: [] as MountIndexReport['indexedFiles'],
					unindexed: [] as MountIndexReport['unindexedFiles']
				}
			);

		console.log('[categorizeFiles] Results:', {
			indexed: indexed.length,
			unindexed: unindexed.length,
			directories: directories.length
		});

		return { indexedFiles: indexed, unindexedFiles: unindexed, directories };
	}

	private calculateStats(
		indexedFiles: MountIndexReport['indexedFiles'],
		unindexedFiles: MountIndexReport['unindexedFiles'],
		directories: MountIndexReport['directories']
	): MountIndexReport['stats'] {
		return {
			total: indexedFiles.length + unindexedFiles.length,
			indexed: indexedFiles.length,
			unindexed: unindexedFiles.length,
			directories: directories.length
		};
	}

	private isImageFile(filename: string): boolean {
		return /\.(jpg|jpeg|png|gif|webp)$/i.test(filename);
	}

	async listFiles(mountId: string, subPath: string = ''): Promise<MountIndexReport> {
		console.log('[listFiles] Starting file listing for:', { mountId, subPath });
		try {
			const mount = await this.getMount(mountId);
			const fullPath = join(mount.path, subPath);

			// Verify path safety
			await this.verifyPathSafety(mountId, subPath);

			// Get indexed files from database
			const indexedFiles = await this.getIndexedFiles(mountId, subPath);

			// Read filesystem
			const allFiles = await this.readFileSystem(fullPath, subPath);

			// Categorize files
			const {
				indexedFiles: indexed,
				unindexedFiles: unindexed,
				directories
			} = this.categorizeFiles(allFiles, indexedFiles);

			// Calculate stats
			const stats = this.calculateStats(indexed, unindexed, directories);

			console.log('[listFiles] Complete:', stats);

			return {
				indexedFiles: indexed,
				unindexedFiles: unindexed,
				directories,
				stats
			};
		} catch (error) {
			console.error('[listFiles] Error:', error);
			throw error;
		}
	}

	async verifyPathSafety(mountId: string, subPath: string) {
		const mount = await this.getMount(mountId);
		const fullPath = join(mount.path, subPath);
		const realPath = resolve(fullPath);
		const mountPath = resolve(mount.path);

		if (!realPath.startsWith(mountPath)) {
			throw new Error('Path is outside mount directory');
		}

		if (!existsSync(realPath)) {
			throw new Error('Path does not exist');
		}

		return realPath;
	}

	async isDirectory(path: string) {
		try {
			const stats = await fs.stat(path);
			return stats.isDirectory();
		} catch (error) {
			throw new Error('Failed to check if path is directory');
		}
	}

	async indexMount(mountId: string) {
		const mount = await this.getMount(mountId);
		const indexer = new ImageIndexer(mount);
		await indexer.indexDirectory(mount.path);
	}

	async reindexAllMounts() {
		const mounts = await this.listMounts();
		for (const mount of mounts) {
			await this.indexMount(mount.id);
		}
	}

	async getMountImages(mountId: string) {
		return await db.query.imageInfo.findMany({
			where: (fields, { eq }) => eq(fields.mountId, mountId),
			orderBy: (fields, { asc }) => [asc(fields.relativePath)]
		});
	}
}

export const mountManager = new MountManager();
