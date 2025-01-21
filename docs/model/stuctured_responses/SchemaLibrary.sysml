package 'SchemaLibrary' {
    doc /* Manages schema compilation, loading, and status tracking for finite state machines.
         Provides centralized schema access and async compilation capabilities. */

    private import ScalarValues::*;
    private import Collections::*;
    private import PyCore::*;
    private import Pydantic::*;

    // Schema Status Tracking
    enum def SchemaStatus {
        NOT_LOADED = "not_loaded";
        LOADING = "loading"; 
        LOADED = "loaded";
        ERROR = "error";
    }

    // Schema Metadata
    part def SchemaMetadata {
        doc /* Metadata for tracking schema state and compilation info */
        
        attribute name : String;
        attribute version : String;
        attribute status : SchemaStatus = SchemaStatus::NOT_LOADED;
        attribute error_message : String;
        attribute last_updated : Time::DateTime;
        attribute dependencies : String[*];
    }

    // Schema Registry Entry
    part def SchemaEntry {
        doc /* Individual schema entry with metadata and compiled schema */
        
        part _metadata : SchemaMetadata;
        item schema : BaseModel;
        item fsm : Any;  // Compiled FSM instance
        
        action validate {
            doc /* Validate data against schema */
            in data : Any;
            out validated : BaseModel;
        }
    }

    // Main Schema Library
    part def SchemaLibrary {
        doc /* Central manager for FSM schemas */
        
        // Registry of schemas
        attribute schemas : Map;  // name -> SchemaEntry
        
        // Thread pool for async operations
        attribute max_workers : Integer = 4;
        
        action register_schema {
            doc /* Register a new schema */
            in name : String;
            in schema : BaseModel;
            in dependencies : String[*];
            out entry : SchemaEntry;
        }
        
        action compile_schema {
            doc /* Asynchronously compile FSM from schema */
            in name : String;
            out status : SchemaStatus;
            
            action update_status {
                in name : String;
                in status : SchemaStatus;
                in error : String;
            }
            
            action compile_async {
                doc /* Compile in separate thread */
                in schema : BaseModel;
                out fsm : Any;
            }
        }
        
        action get_schema {
            doc /* Retrieve schema by name */
            in name : String;
            out schema : SchemaEntry;
        }
        
        action get_status {
            doc /* Get schema compilation status */
            in name : String;
            out status : SchemaStatus;
        }
        
        action wait_for_schema {
            doc /* Wait for schema to finish loading */
            in name : String;
            in timeout : Real;
            out success : Boolean;
        }
        
        action compile_all {
            doc /* Compile all registered schemas */
            out statuses : Map;  // name -> status
        }
    }

    // Schema Events
    item def SchemaEvent {
        doc /* Base event for schema status changes */
        attribute schema_name : String;
        attribute timestamp : Time::DateTime;
    }
    
    item def SchemaLoadedEvent :> SchemaEvent {
        doc /* Event when schema is successfully loaded */
    }
    
    item def SchemaErrorEvent :> SchemaEvent {
        doc /* Event when schema fails to load */
        attribute error : String;
    }

    // Example Usage
    part example {
        doc /* Example implementation */
        
        part library : SchemaLibrary {
            action setup {
                doc /* Initialize library */
                
                // Register schemas
                action register_schema {
                    in name = "user_schema";
                    in schema = UserSchema;
                }
                
                // Compile async
                then action compile_all;
                
                // Wait for critical schemas
                then action wait_for_schema {
                    in name = "user_schema";
                    in timeout = 30.0;
                }
            }
        }
    }
}