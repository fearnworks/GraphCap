package 'GraphCapServer' {
    doc /* Models the GraphCap FastAPI server architecture and components.
         Represents the server endpoints, middleware, and image processing capabilities. */
    

    import ScalarValues::*;
    
    // Data type definitions
    item def UploadFile;
    item def JSON;

    item def ServerController {
        doc /* Controller for GraphCapServer */
        part def ModelInfo {
            doc /* Server model information */
            attribute model_name : ScalarValues::String;
            attribute model_class : ScalarValues::String;
            attribute cuda_device_name : ScalarValues::String;
            attribute cuda_device_count : ScalarValues::Integer;
        }

        action def getModelInfo {
            out info : ModelInfo;
        }

        action def getHealth {
            out status : JSON;
        }
    }



    part def Agent {
        doc /* Agent that processes a task */
    }



    // Server Definition
    part def GraphCapServer :> FastAPI::FastAPI {
        doc /* Main server component handling HTTP requests */
        
        // Server Components
        part structured_caption : DenseGraphCaption::DenseGraphCaptionAgent;
        
        // Override base configuration
        part config : FastAPI::ServerConfig {
            attribute title = "GraphCap API";
            attribute version = "1.0.0";
            attribute debug = false;
        }
        
        // Add CORS configuration
        part cors : FastAPI::CORSConfig {
            attribute allow_origins;
            attribute allow_credentials = true;
        }
        
        // Endpoint Actions
        action generate_caption {
            doc /* Processes image and generates structured caption */
            in file : UploadFile;
            out caption : JSON;
        }   
        
        action health_check {
            doc /* Server health check endpoint */
            out status : JSON;
        }
        
        action model_info {
            doc /* Provides information about the loaded model */
            out info : ModelInfo;
        }
    }

    // Image Processing Interface
    interface def ImageProcessing {
        doc /* Interface for image processing operations */
        end input : PIL::ImagePort;
        end output : PIL::ImagePort;
        
        action process {
            in image : PIL::Image;
            out result : JSON;
        }
    }

    // Server Instance
    part server {
        doc /* Server instance implementation */
        
        part app : GraphCapServer {
            // Server initialization
            action initialize {
                doc /* Initializes server components and CUDA */
                
                action check_cuda {
                    out is_available : Boolean;
                    out device_name : String;
                }
                
                action init_caption_model {
                    out model : DenseGraphCaption::DenseGraphCaptionAgent;
                }
            }
        }
    }
}

