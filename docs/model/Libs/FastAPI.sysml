package 'FastAPI' {
    doc /* Models the core FastAPI server architecture and components.
         Based on the official FastAPI implementation. */
    
    // Import common libraries
    private import ScalarValues::*;
    private import Collections::*;

    // Core type definitions
    item def HTTPException;
    item def Response;
    item def Request;
    item def State;
    item def ASGIApp;

    // Server Configuration
    part def ServerConfig {
        doc /* Core configuration settings for FastAPI server */
        
        attribute debug : Boolean = false {
            doc /* Boolean indicating if debug tracebacks should be returned on errors */
        }
        attribute title : String = "FastAPI" {
            doc /* The title of the API shown in documentation */
        }
        attribute version : String = "0.1.0" {
            doc /* API version string */
        }
        attribute openapi_url : String = "/openapi.json" {
            doc /* URL where the OpenAPI schema will be served */
        }
        attribute docs_url : String = "/docs" {
            doc /* Path to Swagger UI documentation */
        }
        attribute redoc_url : String = "/redoc" {
            doc /* Path to ReDoc documentation */
        }
        attribute root_path : String = "" {
            doc /* Base path prefix for the application */
        }
    }

    // CORS Configuration
    part def CORSConfig {
        doc /* CORS middleware configuration */
        
        attribute allow_origins : String[*];
        attribute allow_methods : String[*];
        attribute allow_headers : String[*];
        attribute allow_credentials : Boolean;
    }

    // Main FastAPI Application
    part def FastAPI {
        doc /* Main FastAPI application class */
        
        // Core attributes
        part config : ServerConfig;
        part cors : CORSConfig;
        attribute openapi_version : String = "3.1.0";
        
        // Core operations
        action setup {
            doc /* Initialize server components and middleware */
        }
        
        action openapi {
            doc /* Generate OpenAPI schema */
            out schema : PyCore::JSON;
        }
        
        // Exception handling
        action handle_exception {
            doc /* Global exception handler */
            in exception : HTTPException;
            out response : Response;
        }
        
        // Middleware handling
        action add_middleware {
            doc /* Add middleware to application */
            in middleware : ASGIApp;
        }
        
        // Route handling
        action add_route {
            doc /* Add new route to application */
            in path : String;
            in endpoint : PyCore::Function;
            in methods : String[*];
        }
    }

    // Route Definition
    part def Route {
        doc /* Represents an API route */
        
        attribute path : String;
        attribute methods : String[*];
        item endpoint : PyCore::Function;
        item response_model : PyCore::Any;
        attribute tags : String[*];
        
        action handle {
            doc /* Handle incoming request */
            in request : Request;
            out response : Response;
        }
    }

    // API Documentation
    part def APIDoc {
        doc /* API documentation configuration */
        
        attribute title : String;
        attribute description : String;
        attribute version : String;
        item openapi_tags : PyCore::JSON;
        item servers : PyCore::JSON[*];
        
        action generate_docs {
            doc /* Generate API documentation */
            out docs : PyCore::JSON;
        }
    }

    // Example Usage
    part example {
        doc /* Example FastAPI server implementation */
        
        part app : FastAPI {
            part config : ServerConfig {
                attribute title = "My API";
                attribute version = "1.0.0";
                attribute debug = true;
            }
            
            action startup {
                doc /* Server startup sequence */
            }
            
            action shutdown {
                doc /* Server shutdown sequence */
            }
        }
    }
}