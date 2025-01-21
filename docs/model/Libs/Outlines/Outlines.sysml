package Outlines {
    part def Sampler {
        /* Sampler settings*/
    }

    part def GenerationState {
        /* Generation state */
        item token_ids : Torch::Tensor;
        item kv_cache : Torch::Tensor;
        item logits : Torch::Tensor;
        item weights : Torch::Tensor;
        attribute fsm_states : Collections::List;
    }

    part def SequenceGenerator {
        in model;
        in schema; 
        in sampler;
    }

    part def JSONGenerator :> SequenceGenerator {
        in schema : Pydantic::BaseModel;
    }

    // Generator components
    part def Generator {
        doc /* Base generator class for handling token generation */
        
        attribute model;  // Language model
        attribute tokenizer;  // Tokenizer for text processing
        attribute max_tokens : Integer = 2048;
        
        action generate {
            doc /* Generate tokens based on input prompt */
            in prompt : String;
            in max_new_tokens : Integer;
            out tokens : Torch::Tensor;
        }
        
        action decode {
            doc /* Decode generated tokens to text */
            in tokens : Torch::Tensor;
            out text : String;
        }
    }

    part def PromptGenerator :> Generator {
        doc /* Generator for handling prompt-based generation */
        
        action format_prompt {
            doc /* Format input prompt with template */
            in template : String;
            in **kwargs : Map;
            out formatted : String;
        }
    }

    part def GenerationState {
        doc /* Maintains state during token generation */
        
        attribute token_ids : Torch::Tensor;
        attribute kv_cache : Torch::Tensor;
        attribute logits : Torch::Tensor;
        attribute weights : Torch::Tensor;
        attribute fsm_states : Collections::List;
        
        action update {
            doc /* Update generation state with new tokens */
            in new_tokens : Torch::Tensor;
            in new_cache : Torch::Tensor;
        }
    }

    part def Sampler {
        doc /* Handles token sampling strategies */
        
        attribute temperature : Real = 1.0;
        attribute top_k : Integer = 0;
        attribute top_p : Real = 1.0;
        
        action sample {
            doc /* Sample next token from logits */
            in logits : Torch::Tensor;
            out token : Torch::Tensor;
        }
    }

    part def SequenceGenerator {
        doc /* Generates sequences using a model and sampler */
        
        in model;
        in schema; 
        in sampler : Sampler;
        
        action generate_sequence {
            doc /* Generate a complete sequence */
            in prompt : String;
            in max_tokens : Integer;
            out sequence : String;
            
            action prepare_inputs {
                doc /* Prepare inputs for model */
                in prompt : String;
                out inputs : Torch::Tensor;
            }
            
            action generate_tokens {
                doc /* Generate tokens step by step */
                in state : GenerationState;
                out tokens : Torch::Tensor;
            }
        }
    }

    part def JSONGenerator :> SequenceGenerator {
        doc /* Specialized generator for JSON output */
        
        in schema : Pydantic::BaseModel;
        
        action validate_output {
            doc /* Validate generated JSON against schema */
            in json_str : String;
            out validated : Pydantic::BaseModel;
        }
    }
}