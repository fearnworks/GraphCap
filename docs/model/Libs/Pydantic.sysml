package 'Pydantic' {
    doc /* This package models the Pydantic validation and data modeling system.
         It provides a structured representation of Pydantic's core model functionality. */
    
    // Import common libraries
    private import ScalarValues::*;
    private import Collections::*;

    // Core type definitions
    item def ValidationError;
    item def JSON;
    item def Dict;
    item def Any;

    // Configuration definition
    part def ConfigDict {
        doc /* Configuration settings for Pydantic models */
        
        attribute from_attributes : Boolean = false;
        attribute validate_assignment : Boolean = true;
        attribute frozen : Boolean = false;
        attribute extra : String = "ignore";  // 'ignore', 'allow', 'forbid'
        attribute str_strip_whitespace : Boolean = false;
        attribute str_to_lower : Boolean = false;
        attribute str_to_upper : Boolean = false;
    }

    // Base Model Definition
    part def BaseModel {
        doc /* Core model class for data validation and settings management.
             Maps to Pydantic's BaseModel class. */
        
        // Configuration
        part model_config : ConfigDict;
        
        // Private attributes
        private attribute __pydantic_extra__ : Map;
        private attribute __pydantic_fields_set__ : Set;
        
        // Core validation actions
        action model_validate {
            doc /* Validates data against the model's schema */
            in data : Any;
            out instance : BaseModel;

        }
        
        action model_validate_json {
            doc /* Validates JSON string data against the model's schema */
            in json_data : String;
            out instance : BaseModel;
        }
        
        action model_dump {
            doc /* Converts the model instance to a dictionary */
            in exclude_unset : Boolean = false;
            in exclude_defaults : Boolean = false;
            out data : Dict;
        }
        
        action model_dump_json {
            doc /* Converts the model instance to a JSON string */
            in exclude_unset : Boolean = false;
            in exclude_defaults : Boolean = false;
            out json : String;
        }
        
        action model_copy {
            doc /* Creates a copy of the model instance */
            in deep : Boolean = false;
            out copy : BaseModel;
        }
    }

    // Field Definition
    part def Field {
        doc /* Provides extra information about model fields */
        
        attribute defaultValue;  // Default value
        attribute fieldAlias : String;  // Alternative name
        attribute fieldTitle : String;  // Field title
        attribute fieldDescription : String;  // Field description
        attribute exclude : Boolean = false;  // Exclude from serialization
        attribute frozen : Boolean = false;  // Make field immutable

        action constructor {
            in value : Any;
            out field : Field;
        }
    }

    // Validator Definition
    part def Validator {
        doc /* Represents field validators */
        
        attribute fields : String[1..*];  // Fields to validate
        attribute mode : String;  // 'before', 'after', or 'wrap'
        attribute check_fields : Boolean = true;
        
        action validate {
            in value : Any;
            out validated : Any;
        }
    }

    // Interface for model validation
    interface def ModelValidation {
        doc /* Standard interface for model validation operations */
        
        end source;
        end target;
        
        action validate {
            in data : Any;
            out validated : BaseModel;
        }
    }

    // Example usage
    part example {
        doc /* Example implementation showing model definition and usage */
        
        part User {
            attribute id : Integer;
            attribute name : String = "John Doe";
            attribute signup_ts : Time::DateTime;
            attribute friends : String[*];
            
            action validate {
                doc /* Validates user data */
                in user_data : Dict;
                out valid_user : User;
            }
        }
    }
}