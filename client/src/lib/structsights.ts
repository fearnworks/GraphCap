export interface ImageTag {
    category: 'Entity' | 'Relationship' | 'Style' | 'Attribute' | 'Composition' | 'Contextual' | 'Technical' | 'Semantic';
    tag: string;
    confidence: number;
}

export interface ImageData {
    tags_list: ImageTag[];
    short_caption: string;
    verification: string;
    dense_caption: string;
}

export interface ScratchPad {
    problem_analysis: string;
    context_analysis: string;
    solution_outline: string;
    solution_plan: string;
}

export interface ChainOfThought {
    scratchpad: ScratchPad;
    response: string;
}

export interface GraphCapResponse<T> {
    content: T;
    error?: string;
}

export interface ServerHealth {
    status: string;
}

export interface ModelInfo {
    model_name: string;
    model_class: string;
    cuda_device_name: string | null;
    cuda_device_count: number;
}

export interface SchemaInfo {
    status: string;
    version: string;
    last_updated: string;
    dependencies: string[];
    error_message?: string;
    has_fsm: boolean;
}

export interface SchemaLibrary {
    [key: string]: SchemaInfo;
}