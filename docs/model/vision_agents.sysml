package 'VisionAgents' {
    doc /* Models the StructuredCaption system for generating structured image captions
         using vision models and outlines generators. */
    
    
    
    // Type definitions
    item def VisionModel;
    item def Sampler;
    item def Generator;
    
    part def StructuredResponse {
        doc /* Structured caption data */
    }
    

    // Main StructuredCaption definition
    part def StructuredVisionAgent {
        doc /* Core component for generating structured captions from images */
        
        // Core components
        part model : VisionModel {
            doc /* Vision model used for image processing */
        }
        
        attribute generators : Collections::Map;
        
        // Initialization
        action initialize {
            doc /* Initialize the StructuredCaption system */
            
            action init_model {
                doc /* Load and initialize the vision model */
                out model : VisionModel;
            }
            
            action init_default_generator {
                doc /* Setup default generator with multinomial sampling */
                in temperature : ScalarValues::Real = 0.5;
                out generator : Generator;
            }
        }
        
        // Generator registration
        action register_generator {
            doc /* Register a new generator with specified configuration */
            in name : ScalarValues::String;
            in sampler : Sampler;
            in schema : Pydantic::BaseModel;
        }
        
        
    }

    // Generator Configuration
    part def GeneratorConfig {
        doc /* Configuration for caption generators */
        
        attribute name : ScalarValues::String;
        attribute temperature : ScalarValues::Real;
        part schema : Pydantic::BaseModel;
        part sampler : Sampler;
    }


   
}