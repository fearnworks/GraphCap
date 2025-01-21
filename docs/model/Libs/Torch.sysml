package 'Torch' {
    doc /* Models PyTorch's core functionality including tensors, neural networks,
         autograd system, and optimization components. */
    import ScalarValues::*;
    // Basic Types and Devices
    item def Device {
        doc /* Represents computation device (CPU/CUDA) */
        attribute type : String;  // 'cpu' or 'cuda'
        attribute index : Integer;
    }
    
    enum def DType {
        doc /* Tensor data types */
        FLOAT32 = "float32";
        FLOAT64 = "float64";
        FLOAT16 = "float16";
        BFLOAT16 = "bfloat16";
        INT32 = "int32";
        INT64 = "int64";
        BOOL = "bool";
    }

    // Tensor Definition
    part def Tensor {
        doc /* Core tensor class representing multi-dimensional arrays */
        
        attribute shape : Integer[*];
        attribute dtype : DType;
        item device : Device;
        attribute requires_grad : Boolean = false;
        item grad : Tensor;
        
        // Basic operations
        action _to {
            doc /* Move tensor to specified device or dtype */
            in target : Device;
            out result : Tensor;
        }
        
        action backward {
            doc /* Compute gradients through autograd */
            in gradient : Tensor;
        }
        
        // Mathematical operations
        action add {
            in other : Tensor;
            out result : Tensor;
        }
        
        action mul {
            in other : Tensor;
            out result : Tensor;
        }
        
        action matmul {
            in other : Tensor;
            out result : Tensor;
        }
    }

    // Neural Network Components
    part def Module {
        doc /* Base class for all neural network modules */
        
        attribute training : Boolean = true;
        
        action forward {
            doc /* Define the computation performed at every call */
            in x : Tensor;
            out result : Tensor;
        }
        
        action parameters {
            doc /* Iterator over module parameters */
            out params : Tensor[*];
        }
        
        action _to {
            doc /* Moves module to specified device */
            in device : Device;
        }
        
        action train {
            doc /* Set training mode */
            in mode : Boolean = true;
        }
        
        action eval {
            doc /* Set evaluation mode */
            in mode : Boolean = false;
        }
    }

    // Common Neural Network Layers
    part def Linear :> Module {
        doc /* Fully connected layer */
        
        attribute in_features : Integer;
        attribute out_features : Integer;
        attribute bias : Boolean = true;
        
        part weight : Tensor;
        part bias_param : Tensor;
    }
    
    part def Conv2d :> Module {
        doc /* 2D convolutional layer */
        
        attribute in_channels : Integer;
        attribute out_channels : Integer;
        attribute kernel_size : Integer[2];
        attribute stride : Integer[2] = [1, 1];
        attribute padding : Integer[2] = [0, 0];
    }

    // Optimization
    part def Optimizer {
        doc /* Base class for all optimizers */
        
        attribute params : Tensor[*];
        attribute defaults : Map;
        
        action step {
            doc /* Performs a single optimization step */
            in closure : Function;
        }
        
        action zero_grad {
            doc /* Clears the gradients of all optimized tensors */
        }
    }
    
    part def SGD :> Optimizer {
        doc /* Stochastic Gradient Descent optimizer */
        
        attribute lr : Real = 0.01;
        attribute momentum : Real = 0.0;
        attribute dampening : Real = 0.0;
        attribute weight_decay : Real = 0.0;
        attribute nesterov : Boolean = false;
    }
    
    part def Adam :> Optimizer {
        doc /* Adam optimizer */
        
        attribute lr : Real = 0.001;
        attribute betas : Real[2] = [0.9, 0.999];
        attribute eps : Real = 1e-8;
        attribute weight_decay : Real = 0.0;
        attribute amsgrad : Boolean = false;
    }

    // Loss Functions
    part def Loss :> Module {
        doc /* Base class for all loss functions */
        
        action forward {
            in prediction : Tensor;
            in target : Tensor;
            out loss : Tensor;
        }
    }
    
    part def CrossEntropyLoss :> Loss {
        doc /* Cross entropy loss for classification */
        attribute weight : Tensor;
        attribute ignore_index : Integer = -100;
        attribute reduction : String = "mean";
    }

    // Utilities
    interface def DataLoader {
        doc /* Interface for loading batches of data */
        
        attribute batch_size : Integer;
        attribute shuffle : Boolean;
        attribute num_workers : Integer;
        
        action iter {
            out batch : Tensor[*];
        }
    }

    // Example Usage
    part example {
        doc /* Example neural network implementation */
        
        part model : Module {
            part layer1 : Linear {
                attribute in_features = 784;
                attribute out_features = 128;
            }
            
            part layer2 : Linear {
                attribute in_features = 128;
                attribute out_features = 10;
            }
            
            action forward {
                in x : Tensor;
                out result : Tensor;
            }
        }
        
        part optimizer : Adam {
            attribute lr = 0.001;
        }
        
        part loss_fn : CrossEntropyLoss;
    }
}