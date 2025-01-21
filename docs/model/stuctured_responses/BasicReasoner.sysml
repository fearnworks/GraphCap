package 'BasicReasoner' {
    doc /* Models the BasicReasoner agent for visual question answering and reasoning.
         Provides structured analysis and chain-of-thought responses to image-based questions. */
    
    private import ScalarValues::*;
    private import Collections::*;
    private import VisionAgents::*;
    private import PIL::*;
    private import VisionWorker::*;
    
    // Core data types
    part def ChainOfThought {
        doc /* Schema for structured reasoning output */
        
        attribute problem_analysis : String;
        attribute context_analysis : String;
        attribute solution_outline : String;
        attribute solution_plan : String[*];
        attribute final_answer : String;
    }

    // Event definitions
    item def ReasoningGeneratedEvent;
    item def ErrorEvent;
    item def RecoveryEvent;
    item def ImageQuestionEvent {
        doc /* Event for image and question input */
        item image : PIL::Image;
        attribute question : String;
    }

    // Main agent definition
    part def BasicReasonerAgent :> StructuredVisionAgent {
        doc /* Agent for generating chain-of-thought reasoning about images */
        
        // Core components
        part model : VisionModel {
            doc /* Vision model used for image processing and reasoning */
        }
        
        part processor : VisionWorker::Processor {
            doc /* Processes inputs and formats instructions */
            
            action format_inputs {
                in instruction : String;
                in question : String;
                in images : PIL::   Image[*];
                out formatted_instruction : String;
            }
        }
        
        part generator : VisionWorker::Generator {
            doc /* Generates structured reasoning output */
            
            attribute temperature : Real = 0.7;
            attribute max_tokens : Integer = 1024;
        }

        // Core operations
        action generate_reasoning {
            doc /* Generate structured reasoning for an image and question */
            
            in image : Image;
            in question : String;
            in instruction : String;
            out reasoning : ChainOfThought;
            
            action format_instruction {
                doc /* Format instruction with image and question context */
                in raw_instruction : String;
                in question : String;
                in images : Image[1..*];
                out formatted : String;
            }
            
            action execute_generator {
                doc /* Execute the reasoning generator */
                in formatted_instruction : String;
                in images : Image[1..*];
                out result : ChainOfThought;
            }
            
            action validate_output {
                doc /* Validate the generated reasoning */
                in reasoning : ChainOfThought;
                out is_valid : Boolean;
            }
        }

        // Processing actions
        action format_instruction {
            in instruction : String;
            in images : Image[*];
            out formatted : String;
        }

        action generate_reasoning_output {
            in formatted_instruction : String;
            in images : PIL::Image[*];
            out result : ChainOfThought;
        }

        action validate_output {
            in reasoning : ChainOfThought;
            out is_valid : Boolean;
        }

        action log_error {
            in error_message : String;
        }

        action clear_error;

        // State definition
        state reasonerStates {
            entry; then idle;
            
            state idle;
            accept ImageQuestionEvent then processing;
            
            state processing {
                entry format_instruction;
                do generate_reasoning_output;
                exit validate_output;
            }
            
            accept ReasoningGeneratedEvent then idle;
            accept ErrorEvent then error;
            
            state error {
                entry log_error;
                exit clear_error;
            }
            accept RecoveryEvent then idle;
        }
    }

    // Constraint definitions
    constraint def ReasoningConstraints {
        doc /* Constraints for reasoning output validation */
        
        in reasoning : ChainOfThought;
        
        assert constraint {
            doc /* Ensure all analysis components are present and non-empty */
            reasoning.problem_analysis != "" and
            reasoning.context_analysis != "" and
            reasoning.solution_outline != "" and
            reasoning.solution_plan != "" and
            reasoning.final_answer != ""
        }
    }

    // Interface definitions
    interface def ReasoningInterface {
        doc /* Interface for reasoning generation */
        
        end input {
            in image : Image;
            in question : String;
        }
        
        end output {
            out reasoning : ChainOfThought;
            out response : String;
        }
        
        flow questionFlow from input.question to output.response;
    }

    // Example usage
    part example {
        doc /* Example implementation */
        
        part reasoner : BasicReasonerAgent {
            // Initialize with default settings
            action setup {
                action initialize;
                then action register_generator {
                    in name : String = "default";
                    in temperature : Real = 0.7;
                }
            }
            
            // Process image and question
            action process_query {
                in image : Image;
                in question : String;
                out reasoning : ChainOfThought;
            }
        }
    }
}