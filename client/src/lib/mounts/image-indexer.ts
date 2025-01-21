import { createHash } from 'crypto';
import { promises as fs } from 'fs';
import { join, relative } from 'path';
import sharp from 'sharp';
import { db } from '$lib/db';
import { imageInfo } from '$lib/db/schema';
import type { Mount } from '$lib/db/schema/mounts';
import type { NewImageInfo } from '$lib/db/schema/image-info';

export class ImageIndexer {
  constructor(private mount: Mount) {}

  async indexDirectory(dirPath: string) {
    const files = await fs.readdir(dirPath, { withFileTypes: true });
    
    for (const file of files) {
      const fullPath = join(dirPath, file.name);
      
      if (file.isDirectory()) {
        await this.indexDirectory(fullPath);
        continue;
      }

      // Only process image files
      if (await this.isImageFile(fullPath)) {
        console.log(`[indexDirectory] Indexing image: ${fullPath}`);
        await this.indexImage(fullPath);
      }
    }
  }

  private async isImageFile(filePath: string): Promise<boolean> {
    try {
      const buffer = await fs.readFile(filePath);
      const metadata = await sharp(buffer).metadata();
      return !!metadata.format; // If we can get format, it's an image
    } catch {
      return false;
    }
  }

  private async indexImage(filePath: string) {
    try {
      const buffer = await fs.readFile(filePath);
      const hash = this.calculateHash(buffer);
      const metadata = await sharp(buffer).metadata();
      const stats = await fs.stat(filePath);
      
      // Get path relative to mount root
      const relativePath = relative(this.mount.path, filePath);

      const imageData: NewImageInfo = {
        hash,
        mountId: this.mount.id,
        relativePath,
        fileSize: stats.size,
        width: metadata.width!,
        height: metadata.height!,
        mimeType: `image/${metadata.format}`,
      };

      // Check if image already exists
      const existing = await db.query.imageInfo.findFirst({
        where: (fields, { and, eq }) => and(
          eq(fields.hash, hash),
          eq(fields.mountId, this.mount.id)
        )
      });

      if (!existing) {
        await db.insert(imageInfo).values(imageData);
      }

      return imageData;
    } catch (error) {
      console.error(`Failed to index image ${filePath}:`, error);
      throw error;
    }
  }

  private calculateHash(buffer: Buffer): string {
    return createHash('sha256').update(buffer).digest('hex');
  }
} 