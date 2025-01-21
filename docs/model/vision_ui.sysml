package 'GraphCapUI' {
    doc /* Models the Svelte-based user interface for the GraphCap image captioning system.
         Represents components, data flow, and user interactions. */
    
    private import 'GraphCapServer';
    
    // Data Types
    item def File;
    







    // API Client
    part def GraphCapClient {
        doc /* Client for communicating with the GraphCap server */
        
        attribute baseUrl : ScalarValues::String = "http://localhost:8000";
        
        action generateCaption {
            doc /* Send image to server for processing */
            in file : File;
            out response : DenseGraphCaption::ImageData;
            
        }
        
        action getModelInfo {
            doc /* Retrieve model information */
            out info : GraphCapServer::ServerController::ModelInfo;
        }
        
        action checkHealth {
            doc /* Check server health status */
            out status : ScalarValues::String;
        }
    }

    // UI Components
    part def ImageUploader {
        doc /* Component for handling image file uploads */
        
        attribute dragOver : ScalarValues::Boolean = false;
        
        action handleDragOver {
            in _event : Web::DragEvent;
        }
        
        action handleDrop {
            in _event : Web::DragEvent;
            out file : File;
        }
        
        action handleFileSelect {
            out file : File;
        }
        
        port upload {
            doc /* Port for emitting selected files */
            out file : File;
        }
    }

    part def ServerStatus {
        doc /* Component for displaying server status */
        attribute status : ScalarValues::String;
        attribute modelInfo : ModelInfo;
    }

    part def ImageDisplay {
        part image : PIL::Image;
        part caption : DenseGraphCaption::ImageData;

        part def CaptionDisplay {
            doc /* Component for displaying caption results */
            attribute caption : DenseGraphCaption::ImageData;
            
        }
    }


    // Main Application
    part def App {
        doc /* Main application component */
        
        // State
        attribute loading : ScalarValues::Boolean = false;
        attribute error : ScalarValues::String;
        attribute modelInfo : ModelInfo;
        attribute caption : DenseGraphCaption::ImageData;
        
        // Components
        part uploader : ImageUploader;
        part display : CaptionDisplay;
        part client : GraphCapClient;
        
        // Actions
        action initialize {
            doc /* Initialize application */
            action loadModelInfo {
                out info : ModelInfo;
            }
        }
        
        action handleUpload {
            doc /* Process image upload */
            in file : File;
            out caption : CaptionResponse;
            
            action setLoading {
                in state : Boolean;
            }
            
            action setError {
                in message : String;
            }
        }
        
        // Interface definition
        interface def DataFlow {
            doc /* Defines data flow between components */
            
            end source : ImageUploader;
            end target : CaptionDisplay;
            
            flow imageData {
                doc /* Image data flow from uploader to display */
                from source;
                to target;
            }
        }
    }

    // Usage Example
    part example {
        doc /* Example implementation */
        
        part app : App {
            action startup {
                first initialize;
                then action connect {
                    doc /* Connect to server */
                }
            }
            
            action processImage {
                first uploader.handleFileSelect;
                then handleUpload;
                then display.render;
            }
        }
    }
}