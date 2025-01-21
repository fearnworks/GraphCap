package 'Web' {
    doc /* Core web components and events model for browser-based UIs.
         Provides base definitions for HTML elements, events, and common patterns. */
    item def Element
    item def Function;
    item def Object;
    item def File;

    // DOM Events
    item def Event {
        doc /* Base event type */
        attribute type : ScalarValues::String;
        attribute target : Element;
        attribute timestamp : Time::DateTime;
        
        action preventDefault;
        action stopPropagation;
    }
    
    item def MouseEvent :> Event {
        doc /* Mouse-related events */
        attribute clientX : ScalarValues::Number;
        attribute clientY : ScalarValues::Number;
        attribute button : ScalarValues::Number;
    }
    
    item def KeyboardEvent :> Event {
        doc /* Keyboard-related events */
        attribute key : ScalarValues::String;
        attribute code : ScalarValues::String;
        attribute ctrlKey : ScalarValues::Boolean;
        attribute shiftKey : ScalarValues::Boolean;
    }
    
    item def DragEvent :> MouseEvent {
        doc /* Drag and drop events */
        part dataTransfer : DataTransfer;
    }

    // HTML Elements
    part def Element {
        doc /* Base HTML element */
        attribute id : ScalarValues::String;
        attribute className : ScalarValues::String;
        attribute style : Object;
        
        action addEventListener {
            in eventType : ScalarValues::String;
            in handler : Function;
        }
        
        action removeEventListener {
            in eventType : ScalarValues::String;
            in handler : Function;
        }
    }
    
    part def HTMLElement :> Element {
        doc /* HTML element with additional properties */
        attribute innerHTML : ScalarValues::String;
        attribute textContent : ScalarValues::String;
        attribute hidden : ScalarValues::Boolean;
        
        action focus;
        action blur;
        action click;
    }
    
    // Form Elements
    part def Input :> HTMLElement {
        doc /* Input element for forms */
        attribute value : ScalarValues::String;
        attribute type : ScalarValues::String;
        attribute placeholder : ScalarValues::String;
        attribute disabled : ScalarValues::Boolean;
        attribute required : ScalarValues::Boolean;
        
        action select;
    }
    
    part def Button :> HTMLElement {
        doc /* Button element */
        attribute disabled : ScalarValues::Boolean;
        attribute type : ScalarValues::String = "button";
    }
    
    // File Handling
    item def File {
        doc /* File object */
        attribute name : ScalarValues::String;
        attribute size : ScalarValues::Number;
        attribute type : ScalarValues::String;
        attribute lastModified : Time::DateTime;
    }
    
    item def FileList {
        doc /* Collection of files */
        attribute length : ScalarValues::Integer;
        
        action item {
            in index : ScalarValues::Integer;
            out file : File;
        }
    }
    
    item def DataTransfer {
        doc /* Data transfer for drag and drop */
        attribute files : FileList;
        attribute types : String[*];
        
        action getData {
            in format : ScalarValues::String;
            out data : ScalarValues::String;
        }
        
        action setData {
            in format : ScalarValues::String;
            in data : ScalarValues::String;
        }
    }

    // Common UI Components
    part def Container :> HTMLElement {
        doc /* Generic container element */
        attribute children : Element[*];
    }
    
    part def Image :> HTMLElement {
        doc /* Image element */
        attribute src : ScalarValues::String;
        attribute alt : ScalarValues::String;
        attribute width : ScalarValues::Integer;
        attribute height : ScalarValues::Integer;
    }
    
    // Event Handling Interface
    interface def EventHandler {
        doc /* Standard interface for event handling */
        
        end source : Element;
        end target : Element;
        
        flow event {
            from source;
            to target;
        }
    }

    // Example Usage
    part example {
        doc /* Example component implementation */
        
        part imageUploader : Container {
            part input : Input {
                attribute type = "file";
                attribute accept = "image/*";
            }
            
            part preview : Image;
            
            action handleFileSelect {
                in event : Event;
                out file : File;
            }
        }
    }
}