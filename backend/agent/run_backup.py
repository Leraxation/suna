import os
import json
import re
from uuid import uuid4
from typing import Optional
import time

# Custom imports for Suna AI tools and utilities
from tools.netlify_deploy_tool import NetlifyDeployTool
from agent.tools.message_tool import MessageTool
from agent.tools.sb_deploy_tool import SandboxDeployTool
from agent.tools.sb_expose_tool import SandboxExposeTool
from agent.tools.web_search_tool import SandboxWebSearchTool
from dotenv import load_dotenv
from utils.config import config
from flags.flags import is_enabled
from agent.agent_builder_prompt import get_agent_builder_prompt
from agentpress.thread_manager import ThreadManager
from agentpress.response_processor import ProcessorConfig
from agent.tools.sb_shell_tool import SandboxShellTool
from agent.tools.sb_files_tool import SandboxFilesTool
from agent.tools.sb_browser_tool import SandboxBrowserTool
from agent.tools.data_providers_tool import DataProvidersTool
from agent.tools.expand_msg_tool import ExpandMessageTool
from agent.prompt import get_system_prompt
from utils.logger import logger
from utils.auth_utils import get_account_id_from_thread
from services.billing import check_billing_status
from agent.tools.sb_vision_tool import SandboxVisionTool
from services.langfuse import langfuse
from langfuse.client import StatefulTraceClient
from agent.gemini_prompt import get_gemini_system_prompt
from agent.tools.mcp_tool_wrapper import MCPToolWrapper
from agentpress.tool import SchemaType

# Load environment variables (critical for API keys to avoid 403 Forbidden errors)
load_dotenv()

# Constants for magic numbers to improve readability and maintainability
RABBITMQ_INIT_DELAY = 30  # Delay in seconds for RabbitMQ queue initialization
MAX_KNOWLEDGE_TOKENS = 4000  # Max tokens for knowledge base context
MAX_ITERATIONS_DEFAULT = 100  # Default max iterations for agent execution
NATIVE_MAX_AUTO_CONTINUES_DEFAULT = 25  # Default max auto-continues for native tools

# Delay to avoid race condition with RabbitMQ queue creation
time.sleep(RABBITMQ_INIT_DELAY)
logger.info(f"Applied {RABBITMQ_INIT_DELAY}s delay for RabbitMQ initialization")

async def run_agent(
    thread_id: str,
    project_id: str,
    stream: bool,
    thread_manager: Optional[ThreadManager] = None,
    native_max_auto_continues: int = NATIVE_MAX_AUTO_CONTINUES_DEFAULT,
    max_iterations: int = MAX_ITERATIONS_DEFAULT,
    model_name: str = "anthropic/claude-sonnet-4-20250514",
    enable_thinking: Optional[bool] = False,
    reasoning_effort: Optional[str] = 'low',
    enable_context_manager: bool = True,
    agent_config: Optional[dict] = None,
    trace: Optional[StatefulTraceClient] = None,
    is_agent_builder: Optional[bool] = False,
    target_agent_id: Optional[str] = None
):
    """Run the development agent with specified configuration.
    
    Args:
        thread_id (str): Unique identifier for the conversation thread.
        project_id (str): Unique identifier for the project.
        stream (bool): Whether to stream responses or not.
        thread_manager (Optional[ThreadManager]): Manager for thread operations.
        native_max_auto_continues (int): Max auto-continues for native tools.
        max_iterations (int): Maximum iterations for agent execution.
        model_name (str): Name of the LLM model to use.
        enable_thinking (Optional[bool]): Enable thinking mode if True.
        reasoning_effort (Optional[str]): Level of reasoning effort ('low', 'high').
        enable_context_manager (bool): Enable context manager if True.
        agent_config (Optional[dict]): Custom configuration for the agent.
        trace (Optional[StatefulTraceClient]): Langfuse trace for monitoring.
        is_agent_builder (Optional[bool]): If True, run in agent builder mode.
        target_agent_id (Optional[str]): Target agent ID for builder mode.
    
    Returns:
        Yields response chunks or status messages during execution.
    """
    logger.info(f"🚀 Starting agent with model: {model_name}")
    if agent_config:
        logger.info(f"Using custom agent: {agent_config.get('name', 'Unknown')}")

    # Initialize tracing if not provided
    if not trace:
        trace = langfuse.trace(
            name="run_agent",
            session_id=thread_id,
            metadata={"project_id": project_id}
        )
    thread_manager = ThreadManager(
        trace=trace,
        is_agent_builder=is_agent_builder,
        target_agent_id=target_agent_id,
        agent_config=agent_config
    )

    client = await thread_manager.db.client

    # Get account ID for billing checks (critical for avoiding 403 errors)
    account_id = await get_account_id_from_thread(client, thread_id)
    if not account_id:
        raise ValueError("Could not determine account ID for thread")

    # Fetch project and sandbox information
    project = await client.table('projects').select('*').eq('project_id', project_id).execute()
    if not project.data or len(project.data) == 0:
        raise ValueError(f"Project {project_id} not found")

    project_data = project.data[0]
    sandbox_info = project_data.get('sandbox', {})
    if not sandbox_info.get('id'):
        raise ValueError(f"No sandbox found for project {project_id}")

    # Tool registration logic
    enabled_tools = None
    if agent_config and 'agentpress_tools' in agent_config:
        enabled_tools = agent_config['agentpress_tools']
        logger.info("Using custom tool configuration from agent")

    # Register tools based on configuration or defaults
    if is_agent_builder:
        logger.info("Agent builder mode - registering only update agent tool")
        from agent.tools.update_agent_tool import UpdateAgentTool
        from services.supabase import DBConnection
        db = DBConnection()
        thread_manager.add_tool(
            UpdateAgentTool,
            thread_manager=thread_manager,
            db_connection=db,
            agent_id=target_agent_id
        )
    elif enabled_tools is None:
        logger.info("No agent specified - registering all tools for full Suna capabilities")
        thread_manager.add_tool(SandboxShellTool, project_id=project_id, thread_manager=thread_manager)
        thread_manager.add_tool(SandboxFilesTool, project_id=project_id, thread_manager=thread_manager)
        thread_manager.add_tool(
            SandboxBrowserTool,
            project_id=project_id,
            thread_id=thread_id,
            thread_manager=thread_manager
        )
        thread_manager.add_tool(SandboxDeployTool, project_id=project_id, thread_manager=thread_manager)
        thread_manager.add_tool(SandboxExposeTool, project_id=project_id, thread_manager=thread_manager)
        thread_manager.add_tool(ExpandMessageTool, thread_id=thread_id, thread_manager=thread_manager)
        thread_manager.add_tool(MessageTool)
        thread_manager.add_tool(SandboxWebSearchTool, project_id=project_id, thread_manager=thread_manager)
        thread_manager.add_tool(
            SandboxVisionTool,
            project_id=project_id,
            thread_id=thread_id,
            thread_manager=thread_manager
        )
        thread_manager.add_tool(NetlifyDeployTool)
        if config.RAPID_API_KEY:
            thread_manager.add_tool(DataProvidersTool)
    else:
        logger.info("Custom agent specified - registering only enabled tools")
        thread_manager.add_tool(ExpandMessageTool, thread_id=thread_id, thread_manager=thread_manager)
        thread_manager.add_tool(MessageTool)
        if enabled_tools.get('sb_shell_tool', {}).get('enabled', False):
            thread_manager.add_tool(SandboxShellTool, project_id=project_id, thread_manager=thread_manager)
        if enabled_tools.get('sb_files_tool', {}).get('enabled', False):
            thread_manager.add_tool(SandboxFilesTool, project_id=project_id, thread_manager=thread_manager)
        if enabled_tools.get('sb_browser_tool', {}).get('enabled', False):
            thread_manager.add_tool(
                SandboxBrowserTool,
                project_id=project_id,
                thread_id=thread_id,
                thread_manager=thread_manager
            )
        if enabled_tools.get('sb_deploy_tool', {}).get('enabled', False):
            thread_manager.add_tool(SandboxDeployTool, project_id=project_id, thread_manager=thread_manager)
        if enabled_tools.get('sb_expose_tool', {}).get('enabled', False):
            thread_manager.add_tool(SandboxExposeTool, project_id=project_id, thread_manager=thread_manager)
        if enabled_tools.get('web_search_tool', {}).get('enabled', False):
            thread_manager.add_tool(SandboxWebSearchTool, project_id=project_id, thread_manager=thread_manager)
        if enabled_tools.get('sb_vision_tool', {}).get('enabled', False):
            thread_manager.add_tool(
                SandboxVisionTool,
                project_id=project_id,
                thread_id=thread_id,
                thread_manager=thread_manager
            )
        if enabled_tools.get('netlify_deploy_tool', {}).get('enabled', False):
            thread_manager.add_tool(NetlifyDeployTool)
        if config.RAPID_API_KEY and enabled_tools.get('data_providers_tool', {}).get('enabled', False):
            thread_manager.add_tool(DataProvidersTool)

    # Register MCP tool wrapper if agent has configured MCPs or custom MCPs
    mcp_wrapper_instance = None
    if agent_config:
        all_mcps = []
        if agent_config.get('configured_mcps'):
            all_mcps.extend(agent_config['configured_mcps'])
        if agent_config.get('custom_mcps'):
            for custom_mcp in agent_config['custom_mcps']:
                custom_type = custom_mcp.get('customType', custom_mcp.get('type', 'sse'))
                mcp_config = {
                    'name': custom_mcp['name'],
                    'qualifiedName': f"custom_{custom_type}_{custom_mcp['name'].replace(' ', '_').lower()}",
                    'config': custom_mcp['config'],
                    'enabledTools': custom_mcp.get('enabledTools', []),
                    'instructions': custom_mcp.get('instructions', ''),
                    'isCustom': True,
                    'customType': custom_type
                }
                all_mcps.append(mcp_config)
        if all_mcps:
            logger.info(
                f"Registering MCP tool wrapper for {len(all_mcps)} MCP servers "
                f"(including {len(agent_config.get('custom_mcps', []))} custom)"
            )
            thread_manager.add_tool(MCPToolWrapper, mcp_configs=all_mcps)
            for tool_name, tool_info in thread_manager.tool_registry.tools.items():
                if isinstance(tool_info['instance'], MCPToolWrapper):
                    mcp_wrapper_instance = tool_info['instance']
                    break
            if mcp_wrapper_instance:
                try:
                    await mcp_wrapper_instance.initialize_and_register_tools()
                    logger.info("MCP tools initialized successfully")
                    updated_schemas = mcp_wrapper_instance.get_schemas()
                    logger.info(f"MCP wrapper has {len(updated_schemas)} schemas available")
                    for method_name, schema_list in updated_schemas.items():
                        if method_name != 'call_mcp_tool':
                            for schema in schema_list:
                                if schema.schema_type == SchemaType.OPENAPI:
                                    thread_manager.tool_registry.tools[method_name] = {
                                        "instance": mcp_wrapper_instance,
                                        "schema": schema
                                    }
                                    logger.info(f"Registered dynamic MCP tool: {method_name}")
                    all_tools = list(thread_manager.tool_registry.tools.keys())
                    logger.info(f"All registered tools after MCP initialization: {all_tools}")
                    mcp_tools = [
                        tool for tool in all_tools
                        if tool not in [
                            'call_mcp_tool', 'sb_files_tool', 'message_tool',
                            'expand_msg_tool', 'web_search_tool', 'sb_shell_tool',
                            'sb_vision_tool', 'sb_browser_tool', 'computer_use_tool',
                            'data_providers_tool', 'sb_deploy_tool', 'sb_expose_tool',
                            'update_agent_tool'
                        ]
                    ]
                    logger.info(f"MCP tools registered: {mcp_tools}")
                except Exception as e:
                    logger.error(f"Failed to initialize MCP tools: {e}")
                    # Continue without MCP tools if initialization fails

    # Prepare system prompt based on model and configuration
    if "gemini-2.5-flash" in model_name.lower() and "gemini-2.5-pro" not in model_name.lower():
        default_system_content = get_gemini_system_prompt()
    else:
        default_system_content = get_system_prompt()

    # Add sample response for non-anthropic models
    if "anthropic" not in model_name.lower():
        sample_response_path = os.path.join(os.path.dirname(__file__), 'sample_responses/1.txt')
        with open(sample_response_path, 'r') as file:
            sample_response = file.read()
        default_system_content = (
            default_system_content +
            "\n\n <sample_assistant_response>" +
            sample_response +
            "</sample_assistant_response>"
        )

    # Handle custom agent system prompt
    if agent_config and agent_config.get('system_prompt'):
        custom_system_prompt = agent_config['system_prompt'].strip()
        system_content = custom_system_prompt
        logger.info(
            f"Using ONLY custom agent system prompt for: "
            f"{agent_config.get('name', 'Unknown')}"
        )
    elif is_agent_builder:
        system_content = get_agent_builder_prompt()
        logger.info("Using agent builder system prompt")
    else:
        system_content = default_system_content
        logger.info("Using default system prompt only")

    # Add knowledge base context if enabled
    if await is_enabled("knowledge_base"):
        try:
            from services.supabase import DBConnection
            kb_db = DBConnection()
            kb_client = await kb_db.client
            kb_result = await kb_client.rpc(
                'get_knowledge_base_context',
                {'p_thread_id': thread_id, 'p_max_tokens': MAX_KNOWLEDGE_TOKENS}
            ).execute()
            if kb_result.data and kb_result.data.strip():
                logger.info(f"Adding knowledge base context to system prompt for thread {thread_id}")
                system_content += (
                    "Here is the user's knowledge base context for this thread:\n\n" +
                    kb_result.data
                )
            else:
                logger.debug(f"No knowledge base context found for thread {thread_id}")
        except Exception as e:
            logger.error(f"Error retrieving knowledge base context for thread {thread_id}: {e}")

    # Add MCP tool information to system prompt if applicable
    if (
        agent_config and
        (agent_config.get('configured_mcps') or agent_config.get('custom_mcps')) and
        mcp_wrapper_instance and
        mcp_wrapper_instance._initialized
    ):
        mcp_info = "\n\n--- MCP Tools Available ---\n"
        mcp_info += "You have access to external MCP (Model Context Protocol) server tools.\n"
        mcp_info += (
            "MCP tools can be called directly using their native function names "
            "in the standard function calling format:\n"
        )
        mcp_info += '<function_calls>\n'
        mcp_info += '<invoke name="{tool_name}">\n'
        mcp_info += '<parameter name="param1">value1</parameter>\n'
        mcp_info += '<parameter name="param2">value2</parameter>\n'
        mcp_info += '</invoke>\n'
        mcp_info += '</function_calls>\n\n'
        mcp_info += "Available MCP tools:\n"
        try:
            registered_schemas = mcp_wrapper_instance.get_schemas()
            for method_name, schema_list in registered_schemas.items():
                if method_name == 'call_mcp_tool':
                    continue
                for schema in schema_list:
                    if schema.schema.get('function', {}).get('name') == method_name:
                        func_info = schema.schema.get('function', {})
                        description = func_info.get('description', 'No description available')
                        server_match = description.find('(MCP Server: ')
                        if server_match != -1:
                            server_end = description.find(')', server_match)
                            server_info = description[server_match:server_end+1]
                        else:
                            server_info = ''
                        mcp_info += f"- **{method_name}**: {description}\n"
                        params = func_info.get('parameters', {})
                        props = params.get('properties', {})
                        if props:
                            mcp_info += f"  Parameters: {', '.join(props.keys())}\n"
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            mcp_info += "- Error loading MCP tool list\n"
        mcp_info += "\n🚨 CRITICAL MCP TOOL RESULT INSTRUCTIONS 🚨\n"
        mcp_info += "When you use ANY MCP (Model Context Protocol) tools:\n"
        mcp_info += (
            "1. ALWAYS read and use the EXACT results returned by the MCP tool\n"
            "2. For search tools: ONLY cite URLs, sources, and information from the actual search results\n"
            "3. For any tool: Base your response entirely on the tool's output - do NOT add external information\n"
            "4. DO NOT fabricate, invent, hallucinate, or make up any sources, URLs, or data\n"
            "5. If you need more information, call the MCP tool again with different parameters\n"
            "6. When writing reports/summaries: Reference ONLY the data from MCP tool results\n"
            "7. If the MCP tool doesn't return enough information, explicitly state this limitation\n"
            "8. Always double-check that every fact, URL, and reference comes from the MCP tool output\n"
        )
        mcp_info += (
            "\nIMPORTANT: MCP tool results are your PRIMARY and ONLY source of truth for external data!\n"
            "NEVER supplement MCP results with your training data or make assumptions beyond what the tools provide.\n"
        )
        system_content += mcp_info

    system_message = {"role": "system", "content": system_content}

    iteration_count = 0
    continue_execution = True

    # Fetch latest user message for tracing
    latest_user_message = await client.table('messages').select('*').eq(
        'thread_id', thread_id
    ).eq('type', 'user').order('created_at', desc=True).limit(1).execute()
    if latest_user_message.data and len(latest_user_message.data) > 0:
        data = latest_user_message.data[0]['content']
        if isinstance(data, str):
            data = json.loads(data)
        trace.update(input=data['content'])

    while continue_execution and iteration_count < max_iterations:
        iteration_count += 1
        logger.info(f"🔄 Running iteration {iteration_count} of {max_iterations}...")

        # Billing check on each iteration
        can_run, message, subscription = await check_billing_status(client, account_id)
        if not can_run:
            error_msg = f"Billing limit reached: {message}"
            trace.event(
                name="billing_limit_reached",
                level="ERROR",
                status_message=(f"{error_msg}")
            )
            yield {
                "type": "status",
                "status": "stopped",
                "message": error_msg
            }
            break

        # Check if last message is from assistant
        latest_message = await client.table('messages').select('*').eq(
            'thread_id', thread_id
        ).in_('type', ['assistant', 'tool', 'user']).order('created_at', desc=True).limit(1).execute()
        if latest_message.data and len(latest_message.data) > 0:
            message_type = latest_message.data[0].get('type')
            if message_type == 'assistant':
                logger.info("Last message was from assistant, stopping execution")
                trace.event(
                    name="last_message_from_assistant",
                    level="DEFAULT",
                    status_message=("Last message was from assistant, stopping execution")
                )
                continue_execution = False
                break

        # Temporary message handling for browser state and image context
        temporary_message = None
        temp_message_content_list = []
        latest_browser_state_msg = await client.table('messages').select('*').eq(
            'thread_id', thread_id
        ).eq('type', 'browser_state').order('created_at', desc=True).limit(1).execute()
        if latest_browser_state_msg.data and len(latest_browser_state_msg.data) > 0:
            try:
                browser_content = latest_browser_state_msg.data[0]["content"]
                if isinstance(browser_content, str):
                    browser_content = json.loads(browser_content)
                screenshot_base64 = browser_content.get("screenshot_base64")
                screenshot_url = browser_content.get("image_url")
                browser_state_text = browser_content.copy()
                browser_state_text.pop('screenshot_base64', None)
                browser_state_text.pop('image_url', None)
                if browser_state_text:
                    temp_message_content_list.append({
                        "type": "text",
                        "text": f"The following is the current state of the browser:\n{json.dumps(browser_state_text, indent=2)}"
                    })
                if 'gemini' in model_name.lower() or 'anthropic' in model_name.lower() or 'openai' in model_name.lower():
                    if screenshot_url:
                        temp_message_content_list.append({
                            "type": "image_url",
                            "image_url": {"url": screenshot_url, "format": "image/jpeg"}
                        })
                        trace.event(
                            name="screenshot_url_added_to_temporary_message",
                            level="DEFAULT",
                            status_message=("Screenshot URL added to temporary message.")
                        )
                    elif screenshot_base64:
                        temp_message_content_list.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{screenshot_base64}"}
                        })
                        trace.event(
                            name="screenshot_base64_added_to_temporary_message",
                            level="WARNING",
                            status_message=("Screenshot base64 added to temporary message. Prefer screenshot_url if available.")
                        )
                    else:
                        logger.warning("Browser state found but no screenshot data.")
                        trace.event(
                            name="browser_state_found_but_no_screenshot_data",
                            level="WARNING",
                            status_message=("Browser state found but no screenshot data.")
                        )
                else:
                    logger.warning("Model is Gemini, Anthropic, or OpenAI, so not adding screenshot to temporary message.")
                    trace.event(
                        name="model_is_gemini_anthropic_or_openai",
                        level="WARNING",
                        status_message=("Model is Gemini, Anthropic, or OpenAI, so not adding screenshot to temporary message.")
                    )
            except Exception as e:
                logger.error(f"Error parsing browser state: {e}")
                trace.event(name="error_parsing_browser_state", level="ERROR", status_message=(f"{e}"))

        # Handle image context messages
        latest_image_context_msg = await client.table('messages').select('*').eq(
            'thread_id', thread_id
        ).eq('type', 'image_context').order('created_at', desc=True).limit(1).execute()
        if latest_image_context_msg.data and len(latest_image_context_msg.data) > 0:
            try:
                image_context_content = (
                    latest_image_context_msg.data[0]["content"]
                    if isinstance(latest_image_context_msg.data[0]["content"], dict)
                    else json.loads(latest_image_context_msg.data[0]["content"])
                )
                base64_image = image_context_content.get("base64")
                mime_type = image_context_content.get("mime_type")
                file_path = image_context_content.get("file_path", "unknown file")
                if base64_image and mime_type:
                    temp_message_content_list.append({
                        "type": "text",
                        "text": f"Here is the image you requested to see: '{file_path}'"
                    })
                    temp_message_content_list.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
                    })
                else:
                    logger.warning(f"Image context found for '{file_path}' but missing base64 or mime_type.")
                await client.table('messages').delete().eq(
                    'message_id', latest_image_context_msg.data[0]["message_id"]
                ).execute()
            except Exception as e:
                logger.error(f"Error parsing image context: {e}")
                trace.event(name="error_parsing_image_context", level="ERROR", status_message=(f"{e}"))

        if temp_message_content_list:
            temporary_message = {"role": "user", "content": temp_message_content_list}

        # Set max_tokens based on model
        max_tokens = None
        if "sonnet" in model_name.lower():
            max_tokens = 8192
        elif "gpt-4" in model_name.lower():
            max_tokens = 4096
        elif "gemini-2.5-pro" in model_name.lower():
            max_tokens = 64000

        generation = trace.generation(name="thread_manager.run_thread")
        try:
            response = await thread_manager.run_thread(
                thread_id=thread_id,
                system_prompt=system_message,
                stream=stream,
                llm_model=model_name,
                llm_temperature=0,
                llm_max_tokens=max_tokens,
                tool_choice="auto",
                max_xml_tool_calls=1,
                temporary_message=temporary_message,
                processor_config=ProcessorConfig(
                    xml_tool_calling=True,
                    native_tool_calling=False,
                    execute_tools=True,
                    execute_on_stream=True,
                    tool_execution_strategy="parallel",
                    xml_adding_strategy="user_message"
                ),
                native_max_auto_continues=native_max_auto_continues,
                include_xml_examples=True,
                enable_thinking=enable_thinking,
                reasoning_effort=reasoning_effort,
                enable_context_manager=enable_context_manager,
                generation=generation
            )
            if isinstance(response, dict) and "status" in response and response["status"] == "error":
                logger.error(f"Error response from run_thread: {response.get('message', 'Unknown error')}")
                trace.event(
                    name="error_response_from_run_thread",
                    level="ERROR",
                    status_message=(f"{response.get('message', 'Unknown error')}")
                )
                yield response
                break

            last_tool_call = None
            agent_should_terminate = False
            error_detected = False
            full_response = ""
            async for chunk in response:
                if isinstance(chunk, dict) and chunk.get('type') == 'status' and chunk.get('status') == 'error':
                    logger.error(f"Error chunk detected: {chunk.get('message', 'Unknown error')}")
                    trace.event(
                        name="error_chunk_detected",
                        level="ERROR",
                        status_message=(f"{chunk.get('message', 'Unknown error')}")
                    )
                    error_detected = True
                    yield chunk
                    continue
                if chunk.get('type') == 'status':
                    try:
                        metadata = chunk.get('metadata', {})
                        if isinstance(metadata, str):
                            metadata = json.loads(metadata)
                        if metadata.get('agent_should_terminate'):
                            agent_should_terminate = True
                            logger.info("Agent termination signal detected in status message")
                            trace.event(
                                name="agent_termination_signal_detected",
                                level="DEFAULT",
                                status_message="Agent termination signal detected in status message"
                            )
                            content = chunk.get('content', {})
                            if isinstance(content, str):
                                content = json.loads(content)
                            if content.get('function_name'):
                                last_tool_call = content['function_name']
                            elif content.get('xml_tag_name'):
                                last_tool_call = content['xml_tag_name']
                    except Exception as e:
                        logger.debug(f"Error parsing status message for termination check: {e}")
                if chunk.get('type') == 'assistant' and 'content' in chunk:
                    try:
                        content = chunk.get('content', '{}')
                        if isinstance(content, str):
                            assistant_content_json = json.loads(content)
                        else:
                            assistant_content_json = content
                        assistant_text = assistant_content_json.get('content', '')
                        full_response += assistant_text
                        if isinstance(assistant_text, str):
                            if '<' in assistant_text and '>' in assistant_text:
                                if len(assistant_text) < 500:
                                    print(assistant_text, end='', flush=True)
                                else:
                                    if '</ask>' in assistant_text:
                                        print("<ask>...</ask>", end='', flush=True)
                                    elif '</complete>' in assistant_text:
                                        print("<complete>...</complete>", end='', flush=True)
                                    elif '</web-browser-takeover>' in assistant_text:
                                        print("<web-browser-takeover>...</web-browser-takeover>", end='', flush=True)
                                    else:
                                        print("<tool_call>...</tool_call>", end='', flush=True)
                            else:
                                print(assistant_text, end='', flush=True)
                    except Exception as e:
                        logger.error(f"Error processing assistant content: {e}")
                        trace.event(
                            name="error_processing_assistant_content",
                            level="ERROR",
                            status_message=(f"{e}")
                        )
                        yield chunk
                        continue
                yield chunk
            if error_detected:
                logger.info("Error detected during streaming, stopping agent execution")
                trace.event(
                    name="error_detected_during_streaming",
                    level="ERROR",
                    status_message="Error detected during streaming, stopping agent execution"
                )
                continue_execution = False
                break
            if agent_should_terminate:
                logger.info(f"Agent termination requested after tool call: {last_tool_call}")
                trace.event(
                    name="agent_termination_requested",
                    level="DEFAULT",
                    status_message=(f"Agent termination requested after tool call: {last_tool_call}")
                )
                continue_execution = False
                break
            if full_response:
                trace.update(output=full_response)
            generation.end()
        except Exception as e:
            error_message = f"Error in run_thread: {str(e)}"
            logger.error(error_message)
            trace.event(name="run_thread_error", level="ERROR", status_message=error_message)
            generation.end()
            yield {
                "type": "status",
                "status": "error",
                "message": error_message
            }
            break