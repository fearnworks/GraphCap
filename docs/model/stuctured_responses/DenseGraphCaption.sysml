package 'DenseGraphCaption' {

    enum def TagType {
        ENTITY = "Entity";
        RELATIONSHIP = "Relationship";
        STYLE = "Style"; 
        ATTRIBUTE = "Attribute";
        COMPOSITION = "Composition";
        CONTEXTUAL = "Contextual";
        TECHNICAL = "Technical";
        SEMANTIC = "Semantic";
    }

    part def ImageData {
        doc /* Schema for structured image caption data */
        attribute tags : Collections::List;
        attribute short_caption : ScalarValues::String;
        attribute _verification : ScalarValues::String;
        attribute dense_caption : ScalarValues::String;
    }
    part def ImageTag {
        doc /* Individual image tag with metadata */
        attribute category : TagType;
        attribute tag : ScalarValues::String {
            doc /* Descriptive keyword or phrase representing the tag */
        }
        attribute confidence : ScalarValues::Number {
            doc /* Confidence score between 0 (exclusive) and 1 (inclusive) */
        }
    }

    part def DenseGraphCaptionAgent :> VisionAgents::StructuredVisionAgent {
        doc /* Agent for generating dense graph captions */
        // Caption generation
        action generate_caption {
            doc /* Generate structured caption for an image */
            in image : PIL::Image;
            in instruction : ScalarValues::String;
            in generator_name : ScalarValues::String = "default";
            out caption : ImageData;
            
            action format_instruction {
                doc /* Format instruction with image context */
                in raw_instruction : ScalarValues::String;
                in images : PIL::Image[1..*];
                out formatted : ScalarValues::String;
            }
            
            action execute_generator {
                doc /* Execute the selected generator */
                in formatted_instruction : ScalarValues::String;
                in images : PIL::Image[1..*];
                out result : ImageData;
            }
        }
    }

     // Usage Example
    part example {
        doc /* Example usage of StructuredCaption */
        
        part captioner : DenseGraphCaptionAgent {
            // Initialize with default settings
            action setup {
                action initialize;
                then action register_generator {
                    in name : ScalarValues::String = "default";
                    in temperature : ScalarValues::Real = 0.5;
                }
            }
            
            // Generate caption
            action process_image {
                in image : PIL::Image;
                out caption : ImageData;
            }
        }
    }

}