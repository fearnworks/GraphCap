package 'DB' {
    doc /* Models the database schema and data types for GraphCap.
         Uses an image-centric design with offset annotations. */
    
    private import ScalarValues::*;
    private import Collections::*;
    private import Time::*;

    // Core Image Storage
    part def ImageInfo {
        doc /* Core image information and file details */
        
        attribute id : String {
            doc /* UUID for unique image identification */
        }
        attribute hash : String {
            doc /* Cryptographic hash of image content */
        }
        attribute mountId : String {
            doc /* References Mount.id for base path */
        }
        attribute relativePath : String {
            doc /* Path relative to mount point */
        }
        attribute fileSize : Integer {
            doc /* Size in bytes */
        }
        attribute width : Integer {
            doc /* Image width in pixels */
        }
        attribute height : Integer {
            doc /* Image height in pixels */
        }
        attribute mimeType : String {
            doc /* Image MIME type */
        }
        attribute createdAt : DateTime;
        attribute updatedAt : DateTime;

        // Derived full path
        calc def getFullPath {
            in mountPath : String;
            return : String = mountPath + "/" + relativePath;
        }
    }

    // Mount Configuration
    part def Mount {
        doc /* Mount point configuration for data sources */
        
        attribute id : String {
            doc /* UUID for mount identification */
        }
        attribute name : String;
        attribute description : String[0..1];
        attribute basePath : String {
            doc /* Base filesystem path for this mount */
        }
        attribute type : String {
            doc /* Mount type (e.g., 'local', 's3', etc.) */
        }
        attribute createdAt : DateTime;
        attribute updatedAt : DateTime;
    }

    // Base Annotation Definition
    abstract part def Annotation {
        doc /* Base type for all image annotations */
        
        attribute id : String {
            doc /* UUID for annotation */
        }
        attribute imageId : String {
            doc /* References ImageInfo.id */
        }
        attribute createdAt : DateTime;
        attribute updatedAt : DateTime;
    }

    // Annotation Types
    enum def TagCategory {
        doc /* Valid categories for image tags */
        Entity;
        Relationship;
        Style;
        Attribute;
        Composition;
        Contextual;
        Technical;
        Semantic;
    }

    // Specific Annotation Types
    part def ImageTag :> Annotation {
        doc /* Individual tag annotation */
        
        attribute category : TagCategory;
        attribute tag : String;
        attribute confidence : Real {
            doc /* Confidence score between 0 and 1 */
            assert constraint { confidence > 0.0 and confidence <= 1.0 }
        }
    }

    part def CaptionAnnotation :> Annotation {
        doc /* Caption data as an annotation */
        
        attribute shortCaption : String;
        attribute verification : String;
        attribute denseCaption : String;
        
        part tags : ImageTag[*] {
            doc /* Associated tags for this caption */
        }
    }

    part def ChainOfThoughtAnnotation :> Annotation {
        doc /* Reasoning chain as an annotation */
        
        attribute problemAnalysis : String;
        attribute contextAnalysis : String;
        attribute solutionOutline : String;
        attribute solutionPlan : String;
        attribute response : String;
    }

    // Mount Configuration
    part def Mount {
        doc /* Mount point configuration for data sources */
        
        attribute id : String {
            doc /* UUID for mount identification */
        }
        attribute name : String;
        attribute description : String[0..1];
        attribute path : String;
        attribute type : String {
            doc /* Mount type (e.g., 'local') */
        }
        attribute createdAt : DateTime;
        attribute updatedAt : DateTime;
    }

    // Database Interface
    interface def DatabaseOperations {
        doc /* Core database operations interface */
        
        // Mount Operations
        action saveMountPoint {
            in mount : Mount;
            out saved : Mount;
        }
        
        action getMountPoint {
            in id : String;
            out mount : Mount[0..1];
        }
        
        // Image Operations
        action saveImage {
            in info : ImageInfo;
            out saved : ImageInfo;
        }
        
        action getImage {
            in id : String;
            out image : ImageInfo[0..1];
            out mount : Mount[0..1];
        }
        
        // Annotation Operations
        action saveAnnotation {
            in annotation : Annotation;
            out saved : Annotation;
        }
        
        action getAnnotations {
            in imageId : String;
            in type : String[0..1];  // Optional filter by annotation type
            out annotations : Annotation[*];
        }
        
        action getImageWithAnnotations {
            in imageId : String;
            out image : ImageInfo[0..1];
            out mount : Mount[0..1];
            out annotations : Annotation[*];
        }
    }

    // Constraints
    constraint def DataConstraints {
        doc /* Core data validation constraints */
        
        in info : ImageInfo;
        in mount : Mount;
        
        assert constraint validDimensions {
            doc /* Ensure valid image dimensions */
            info.width > 0 and
            info.height > 0
        }
        
        assert constraint validPaths {
            doc /* Ensure paths are provided and mount exists */
            info.relativePath != "" and
            mount.basePath != "" and
            info.mountId == mount.id
        }
        
        assert constraint validHash {
            doc /* Ensure hash is provided */
            info.hash != ""
        }
    }

    // Example Usage
    part example {
        doc /* Example database operations */
        
        action processNewImage {
            in mountId : String;
            in relativePath : String;
            
            // Get mount info
            action getMountInfo {
                in mountId;
                out mount : Mount;
            }
            
            // Create image info
            action createImageInfo {
                in relativePath;
                in mountId;
                out info : ImageInfo;
            }
            
            // Validate and save
            assert constraint DataConstraints {
                in info = createImageInfo::info;
                in mount = getMountInfo::mount;
            }
            
            // Save to database
            perform action saveImage {
                in info = createImageInfo::info;
                out saved : ImageInfo;
            }
            
            // Create initial annotations
            perform action saveAnnotation {
                in annotation : CaptionAnnotation {
                    attribute :>> imageId = saved.id;
                }
            }
        }
    }
} 