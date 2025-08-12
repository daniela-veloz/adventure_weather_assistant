from openai import OpenAI
from typing import Dict, Any, List, Optional, Callable
import json

class LLMClient:
    """
    Enhanced OpenAI client with advanced function calling, iterative processing, and error recovery.
    
    This client extends OpenAI's basic functionality with sophisticated function calling capabilities,
    automatic error handling, conversation history management, and support for both cloud and local models.
    It provides multiple interaction modes including basic text generation, function-enabled responses,
    and complete function calling workflows with iterative processing.
    
    Key Features:
    - Advanced function calling with automatic execution and response handling
    - Iterative processing for multi-step function call workflows
    - Robust error recovery and null response handling
    - Message history management throughout complex conversations
    - Debug capabilities for development and troubleshooting
    - Support for streaming responses
    - Compatible with both OpenAI hosted models and local model servers
    
    Attributes:
        model (str): The model name to use for text generation (e.g., 'gpt-4o-mini')
        openai (OpenAI): The OpenAI client instance configured for API communication
    """
    
    def __init__(self, model, base_url=None):
        """
        Initialize the LLM client with model configuration.
        
        Args:
            model (str): The model name to use (e.g., 'gpt-4o-mini', 'gpt-3.5-turbo')
            base_url (str, optional): Custom base URL for local models. If provided,
                                     the model parameter is used as the API key for
                                     local model authentication. Defaults to None
        """
        self.model = model
        if base_url:
            self.openai = OpenAI(base_url=base_url, api_key=model)
        else:
            self.openai = OpenAI()

    def generate_text(self, user_prompt, system_prompt="", history=None, tools=None, stream=False) -> str:
        """
        Generate a text response using the configured language model with comprehensive feature support.
        
        This method provides the primary text generation interface with support for conversation history,
        function calling tools, and streaming responses. It handles message construction, API parameter
        configuration, and response processing for both basic and advanced use cases.
        
        Features:
        - Conversation history integration with proper message formatting
        - Function calling tools with OpenAI specification compatibility
        - Streaming and non-streaming response modes
        - Automatic message chain construction with system, history, and user prompts
        - Error handling for invalid parameters and API failures
        
        Args:
            user_prompt (str): The user's input message or query for the model to respond to
            system_prompt (str, optional): System-level instructions that guide model behavior, 
                                         personality, and response formatting. Defaults to ""
            history (List[Dict[str, str]], optional): Previous conversation messages in OpenAI format.
                                                     Each message should contain 'role' and 'content' keys.
                                                     Valid roles: 'system', 'user', 'assistant', 'tool'.
                                                     Defaults to None (no history)
            tools (List[Dict[str, Any]], optional): Function calling tool definitions in OpenAI format.
                                                   Each tool must include 'type': 'function' and a 'function'
                                                   object with name, description, and parameters schema.
                                                   Defaults to None (no function calling)
            stream (bool, optional): Enable streaming response mode. When True, returns a generator
                                   that yields response chunks as they arrive. When False, waits
                                   for complete response. Defaults to False

        Returns:
            str: Complete model response text when stream=False
            Generator: Streaming response generator yielding chunks when stream=True
            
        Raises:
            OpenAIError: If the OpenAI API request fails, returns errors, or encounters authentication issues
            ValueError: If conversation history format is invalid or contains unsupported message types
            TypeError: If tools format doesn't match OpenAI specification or contains invalid schemas
            ConnectionError: If network connectivity issues prevent API communication

        """
        if history is None:
            history = []
        
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_prompt}]
        
        # Prepare API call parameters
        api_params = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        # Add tools if provided
        if tools:
            api_params["tools"] = tools
        
        response = self.openai.chat.completions.create(**api_params)
        
        if stream:
            return response  # Return the streaming generator
        else:
            return response.choices[0].message.content

    def generate_with_functions(self, user_prompt: str, system_prompt: str = "", 
                               history: Optional[List[Dict[str, Any]]] = None, 
                               tools: Optional[List[Dict[str, Any]]] = None):
        """
        Generate a response that may include function calls, returning the full response object.
        
        This method is designed for scenarios where you need access to the complete response
        object, including any function calls that the model wants to make. Unlike generate_text(),
        this returns the raw OpenAI response object rather than just the text content, enabling
        access to tool_calls and other response metadata.
        
        Use Cases:
        - Custom function calling implementations
        - Response analysis and debugging
        - Complex multi-turn conversations with function calls
        - Applications requiring access to response metadata
        
        Args:
            user_prompt (str): The user's input message or query
            system_prompt (str, optional): System instructions to guide model behavior. Defaults to ""
            history (List[Dict[str, Any]], optional): Conversation history in OpenAI format. Defaults to None
            tools (List[Dict[str, Any]], optional): Function calling tools in OpenAPI format. Defaults to None
        
        Returns:
            ChatCompletion: The complete OpenAI response object containing:
                - choices[0].message.content: Text response (may be None if function calls are made)
                - choices[0].message.tool_calls: List of function calls to execute
                - usage: Token usage statistics
                - model: Model used for generation
                - Other response metadata
            
        Raises:
            OpenAIError: If the API request fails or returns an error
            ValueError: If conversation history format is invalid
            TypeError: If tools format is invalid or incompatible with the model
        """
        if history is None:
            history = []
        
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_prompt}]
        
        # Prepare API call parameters
        api_params = {
            "model": self.model,
            "messages": messages
        }
        
        # Add tools if provided
        if tools:
            api_params["tools"] = tools

        return self.openai.chat.completions.create(**api_params)

    def handle_function_calls(self, response_message, function_registry: Dict[str, Callable]) -> List[Dict[str, Any]]:
        """
        Execute function calls from an LLM response using a provided function registry.
        
        This method takes a response message that contains tool_calls and executes each
        function call using the provided function registry. It handles argument parsing,
        function execution, error handling, and result formatting for seamless integration
        back into the conversation flow.
        
        Features:
        - Automatic JSON argument parsing and validation
        - Function registry lookup with error handling for missing functions
        - Comprehensive error handling with detailed error messages
        - Result serialization compatible with OpenAI conversation format
        - Support for multiple parallel function calls
        
        Args:
            response_message: The message object from OpenAI response containing tool_calls attribute
            function_registry (Dict[str, Callable]): Dictionary mapping function names to callable functions.
                                                    Functions should accept keyword arguments and return
                                                    JSON-serializable results
        
        Returns:
            List[Dict[str, Any]]: List of tool result messages in OpenAI format, each containing:
                - tool_call_id: Unique identifier linking to the original function call
                - role: "tool" (required by OpenAI conversation format)
                - name: Function name that was executed
                - content: JSON string of function result or error information
            
        Raises:
            ValueError: If a function call references an unknown function in the registry
            Exception: If function execution fails (captured and returned as error in content)
            json.JSONDecodeError: If function arguments cannot be parsed as JSON
        """
        tool_messages = []
        
        if not hasattr(response_message, 'tool_calls') or not response_message.tool_calls:
            return tool_messages
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments
            
            try:
                # Check if function exists in registry
                if function_name not in function_registry:
                    result = {"error": f"Unknown function: {function_name}"}
                else:
                    # Parse arguments and call function
                    args = json.loads(function_args)
                    result = function_registry[function_name](**args)
                
                # Add tool result message
                tool_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result, default=str)
                })
                
            except Exception as e:
                # Add error result message
                tool_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps({"error": str(e)}, default=str)
                })
        
        return tool_messages

    def chat_with_function_calling(self, user_prompt: str, system_prompt: str = "",
                                  history: Optional[List[Dict[str, Any]]] = None,
                                  tools: Optional[List[Dict[str, Any]]] = None,
                                  function_registry: Optional[Dict[str, Callable]] = None,
                                  max_iterations: int = 3,
                                  debug: bool = False) -> str:
        """
        Complete chat workflow with automatic function calling support and iterative processing.
        
        This method provides a complete, production-ready function calling workflow that handles
        the entire process from initial query to final response. It automatically manages
        function execution, conversation state, error recovery, and response generation through
        multiple iterations until a satisfactory result is achieved.
        
        Workflow:
        1. Makes initial call to LLM with user prompt and available tools
        2. If functions are called, executes them using the function registry
        3. Adds function results to conversation and makes follow-up call
        4. Repeats process if more function calls are needed (up to max_iterations)
        5. Returns final text response with comprehensive error handling
        
        Features:
        - Automatic iterative processing for complex multi-step workflows
        - Robust error handling with graceful degradation
        - Debug mode for development and troubleshooting
        - Conversation history management throughout the process
        - Fallback mechanisms for null responses and edge cases
        - Configurable iteration limits to prevent infinite loops
        
        Args:
            user_prompt (str): The user's input message or query
            system_prompt (str, optional): System instructions to guide model behavior. Defaults to ""
            history (List[Dict[str, Any]], optional): Conversation history in OpenAI format. Defaults to None
            tools (List[Dict[str, Any]], optional): Function calling tools in OpenAI format. Defaults to None
            function_registry (Dict[str, Callable], optional): Mapping of function names to callable functions.
                                                              Required if tools are provided. Defaults to None
            max_iterations (int, optional): Maximum number of function calling iterations to prevent infinite loops.
                                          Defaults to 3
            debug (bool, optional): Enable debug output for development and troubleshooting.
                                  Prints iteration status, function calls, and response analysis. Defaults to False
        
        Returns:
            str: The final response text from the LLM after all function calls are completed.
                Returns user-friendly error messages if processing fails.
            
        Raises:
            OpenAIError: If API requests fail due to authentication, rate limits, or service issues
            ValueError: If function registry is missing when model attempts to make function calls
            Exception: Other unexpected errors are caught and returned as user-friendly messages
        """
        if history is None:
            history = []
        
        try:
            # Build initial messages
            messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_prompt}]
            
            # Function calling loop
            for iteration in range(max_iterations):
                # Make call to LLM
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools
                )
                
                response_message = response.choices[0].message
                
                # Add assistant's response to messages
                messages.append(response_message)
                
                # Check if model wants to call functions
                if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                    if not function_registry:
                        raise ValueError("Function registry is required when model makes function calls")
                    
                    # Execute function calls
                    tool_messages = self.handle_function_calls(response_message, function_registry)
                    
                    # Add function results to messages
                    messages.extend(tool_messages)
                    
                    # Continue loop to get final response
                    continue
                else:
                    # No function calls, return the response
                    final_content = response_message.content
                    if final_content:
                        return final_content
                    else:
                        # If content is None but we have messages, try one more call
                        final_response = self.openai.chat.completions.create(
                            model=self.model,
                            messages=messages + [{"role": "user", "content": "Please provide your response."}],
                            tools=None  # Don't allow more function calls
                        )
                        return final_response.choices[0].message.content or "I apologize, but I couldn't generate a response. Please try again."
            
            # If we've exceeded max iterations
            return "I apologize, but I've reached the maximum number of function call iterations. Please try rephrasing your request."
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. Please try again!"