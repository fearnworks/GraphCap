package VisionWorker {
    import ScalarValues::*;
    import Collections::*;

    part def OutputSchema :> Pydantic::BaseModel {
        /* Defines the schema for the output of the model. */
        
    }

    part def Processor {
        attribute model_name: String;
        attribute model_class: String;

        action format_inputs{
            /* Formats the input instruction and images for the model. */
            in instruction: String;
            in images: PIL::Image[*];
            out formatted_instruction: String;
        }
    }

    part def Generator {

    }


    part def Model {
        attribute model_name: String;
        attribute model_class: String;
        part processor: Processor;
    
    }

    
    part def VisionModelController {
        part Model :> Model;
        part Generator :> Generator;
    }



}