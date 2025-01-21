package 'PIL' {
    doc /* This package encapsulates the Python Pillow (PIL) Image class functionality in SysML v2.
         It provides a structured model for image handling and processing operations. */
    
    // Import common libraries
    private import ScalarValues::*;
    private import SI::*;

    item def bytes;
    item def filepointer;

    attribute def ResamplingFilter :> Integer {
        doc /* Defines the resampling filter to use for image resizing. */
        NEAREST = 0;  // Fastest but lowest quality
        LANCZOS = 1;  // Highest quality but slowest
        BILINEAR = 2; // Good balance for downscaling
        BICUBIC = 3;  // Good balance for upscaling
        BOX = 4;     // Good for downscaling
        HAMMING = 5; // Modified BOX filter
    }

    // Core Image Definition
    part def Image {
        doc /* Core representation of an image object.
             Represents both file-based and memory-based images with their properties
             and operations. Maps directly to PIL.Image class. */
        
        // Basic attributes
        attribute filename : String;
        attribute format : String;
        attribute mode : String;
        attribute size : Integer[2];
        attribute width : Integer;
        attribute height : Integer;
        attribute is_animated : Boolean = false;
        attribute n_frames : Integer = 1;
        attribute info : String;

        action get_exif {
            doc /* Returns the EXIF metadata of the image. */
            out exif : Exif;
        }
        part def Exif {
            doc /* Provides read and write access to EXIF image data.
                 Allows accessing, modifying, iterating over and deleting EXIF metadata.
                 Maps to PIL.Image.Exif class which inherits from MutableMapping. */
            
            // Basic attributes
            attribute bigtiff : Boolean = false;
            attribute endian : String;
            
            // Core operations
            action get_ifd {
                doc /* Returns a dictionary containing EXIF data for a specific IFD tag.
                     IFD tags include Exif, GPSInfo, Makernote, Interop and IFD1. */
                in tag : Integer;
                out ifd_data : Collections::Map;
            }
            
            action hide_offsets {
                doc /* Hides offset information in the EXIF data. */
            }
            
            action load {
                doc /* Loads EXIF data from bytes. */
                in data : bytes;
            }
            
            action load_from_fp {
                doc /* Loads EXIF data from a file pointer. */
                in fp : filepointer;
                in offset : Integer;
            }
            
            action tobytes {
                doc /* Converts EXIF data to bytes representation. */
                in offset : Integer = 8;
                out data : bytes;
            }
            
            action items {
                doc /* Returns the items of the EXIF metadata as key-value pairs.
                     Allows iteration over all EXIF tags and their values. */
                out items : Collections::List;
            }
        }
        
        // Core operations as actions
        action open {
            doc /* Opens and identifies the given image file.
                 This is a factory method that returns a new Image instance. */
            in fp : filepointer;  // filepath
            in mode : String = "r";
            out image : Image;
        }

        action save {
            doc /* Saves the image under the given filename. 
                 The format is determined from the filename extension. */
            in filepath : String;
            in format : String;
        }

        action show {
            doc /* Displays the image using the default system image viewer.
                 This is primarily for debugging purposes. */
        }

        // Image processing actions
        action rotate {
            doc /* Returns a rotated copy of the image.
                 The angle is given in degrees counter-clockwise. */
            in angle : Real;
            out rotated : Image;
        }

        action resize {
            doc /* Returns a resized copy of the image.
                 The size is given as a tuple of (width, height).
                 The resample parameter determines the resampling filter. */
            in newSize : Integer[2];
            in resample : ResamplingFilter = ResamplingFilter::BICUBIC;
            out resized : Image;
        }

        action crop {
            doc /* Returns a rectangular region from this image.
                 The box is a 4-tuple defining left, top, right, and bottom coordinates. */
            in box : Integer[4];  // left, top, right, bottom
            out cropped : Image;
        }

        action thumbnail {
            doc /* Creates a thumbnail by resizing the image with best quality settings.
                 This is a more efficient version of resize for creating thumbnails. */
            in size : Integer[2];
            out thumb : Image;
        }
    }



    enum def ImageMode {
        doc /* Defines the pixel format used by the image.
             Each mode represents a different way of storing pixel data. */
        L;      // 8-bit pixels, grayscale
        RGB;    // 3x8-bit pixels, true color
        RGBA;   // 4x8-bit pixels, true color with transparency
        CMYK;   // 4x8-bit pixels, color separation
        P;      // 8-bit pixels, mapped to any other mode using a color palette
    }

    port def ImagePort {
        doc /* Port definition for image data transfer */
        in image : Image;
        out outputImage : Image;
    }

    // Interface definition for image operations
    interface def ImageProcessing {
        doc /* Defines a standard interface for image processing operations.
             Provides a consistent way to handle image transformations. */
        end source : ImagePort;
        end target : ImagePort;
        
        action process {
            doc /* Generic image processing action.
                 Takes a source image and produces a processed output image. */
            in sourceImage : Image;
            out processedImage : Image;
        }
    }

    // Example usage
    use case imageProcessor {
        doc /* Example implementation showing how to chain multiple image
             processing operations together. */
             
        // Create new image
        action createImage {
            doc /* Creates a new image instance from a file. */
            in fp = "example.jpg";
            out outputImage : Image;
        }

        // Process sequence
        action processImage {
            doc /* Demonstrates a sequence of image processing operations:
                 1. Create image from file
                 2. Resize to 800x600
                 3. Rotate 90 degrees
                 4. Save result */
            
            
            action createImage;
            then action resize {    
                in newSize = (800, 600);
            }
            then action rotate {
                in angle = 90;
            }
            then action save {
                in filepath = "processed.jpg";
                in format = "JPEG";
            }
        }
    }
}