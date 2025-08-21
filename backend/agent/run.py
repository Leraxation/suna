import os
import json
import asyncio
import datetime
from typing import Optional, Dict, List, Any, AsyncGenerator
from dataclasses import dataclass

<<<<<<< HEAD
from agent.tools.file_converter import FileConverterTool
=======
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
from agent.tools.message_tool import MessageTool
from agent.tools.sb_deploy_tool import SandboxDeployTool
from agent.tools.sb_expose_tool import SandboxExposeTool
from tools.netlify_deploy_tool import NetlifyDeployTool
from agent.tools.web_search_tool import SandboxWebSearchTool
from dotenv import load_dotenv
from utils.config import config
from agent.agent_builder_prompt import get_agent_builder_prompt
from agentpress.thread_manager import ThreadManager
from agentpress.response_processor import ProcessorConfig
from agent.tools.sb_shell_tool import SandboxShellTool
from agent.tools.sb_files_tool import SandboxFilesTool
from agent.tools.data_providers_tool import DataProvidersTool
from agent.tools.expand_msg_tool import ExpandMessageTool
from agent.prompt import get_system_prompt

from utils.logger import logger
from utils.auth_utils import get_account_id_from_thread
from services.billing import check_billing_status
from agent.tools.sb_vision_tool import SandboxVisionTool
<<<<<<< HEAD
from agent.tools.ai_enhancement_tool import AIEnhancementTool
from agent.tools.data_processing_tool import DataProcessingTool
from agent.tools.integration_tool import IntegrationTool
from agent.tools.storage_security_tool import StorageSecurityTool
from agent.tools.monitoring_maintenance_tool import MonitoringMaintenanceTool
from agent.tools.cognitive_capabilities_tool import CognitiveCapabilitiesTool
from agent.tools.specialized_intelligence_tool import SpecializedIntelligenceTool
from agent.tools.advanced_interaction_tool import AdvancedInteractionTool
from services.langfuse import langfuse
from langfuse.client import StatefulTraceClient
from agent.gemini_prompt import get_gemini_system_prompt
=======
from agent.tools.sb_image_edit_tool import SandboxImageEditTool
from agent.tools.sb_presentation_outline_tool import SandboxPresentationOutlineTool
from agent.tools.sb_presentation_tool_v2 import SandboxPresentationToolV2
from services.langfuse import langfuse
from langfuse.client import StatefulTraceClient

>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
from agent.tools.mcp_tool_wrapper import MCPToolWrapper
from agent.tools.task_list_tool import TaskListTool
from agentpress.tool import SchemaType
from agent.tools.sb_sheets_tool import SandboxSheetsTool
from agent.tools.sb_web_dev_tool import SandboxWebDevTool

load_dotenv()


@dataclass
class AgentConfig:
    thread_id: str
    project_id: str
    stream: bool
    native_max_auto_continues: int = 25
    max_iterations: int = 100
    model_name: str = "openai/gpt-5-mini"
    enable_thinking: Optional[bool] = False
    reasoning_effort: Optional[str] = 'low'
    enable_context_manager: bool = True
    agent_config: Optional[dict] = None
    trace: Optional[StatefulTraceClient] = None
    is_agent_builder: Optional[bool] = False
    target_agent_id: Optional[str] = None


class ToolManager:
    def __init__(self, thread_manager: ThreadManager, project_id: str, thread_id: str):
        self.thread_manager = thread_manager
        self.project_id = project_id
        self.thread_id = thread_id
    
    def register_all_tools(self, agent_id: Optional[str] = None, disabled_tools: Optional[List[str]] = None):
        """Register all available tools by default, with optional exclusions.
        
        Args:
            agent_id: Optional agent ID for agent builder tools
            disabled_tools: List of tool names to exclude from registration
        """
        disabled_tools = disabled_tools or []
        
        logger.debug(f"Registering tools with disabled list: {disabled_tools}")
        
        # Core tools - always enabled
        self._register_core_tools()
        
        # Sandbox tools
        self._register_sandbox_tools(disabled_tools)
        
        # Data and utility tools
        self._register_utility_tools(disabled_tools)
        
        # Agent builder tools - register if agent_id provided
        if agent_id:
            self._register_agent_builder_tools(agent_id, disabled_tools)
        
        # Browser tool
        self._register_browser_tool(disabled_tools)
        
        logger.debug(f"Tool registration complete. Registered tools: {list(self.thread_manager.tool_registry.tools.keys())}")
    
    def _register_core_tools(self):
        """Register core tools that are always available."""
        self.thread_manager.add_tool(ExpandMessageTool, thread_id=self.thread_id, thread_manager=self.thread_manager)
        self.thread_manager.add_tool(MessageTool)
        self.thread_manager.add_tool(TaskListTool, project_id=self.project_id, thread_manager=self.thread_manager, thread_id=self.thread_id)
    
    def _register_sandbox_tools(self, disabled_tools: List[str]):
        """Register sandbox-related tools."""
        sandbox_tools = [
            ('sb_shell_tool', SandboxShellTool, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('sb_files_tool', SandboxFilesTool, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('sb_deploy_tool', SandboxDeployTool, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('sb_expose_tool', SandboxExposeTool, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('web_search_tool', SandboxWebSearchTool, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('sb_vision_tool', SandboxVisionTool, {'project_id': self.project_id, 'thread_id': self.thread_id, 'thread_manager': self.thread_manager}),
            ('sb_image_edit_tool', SandboxImageEditTool, {'project_id': self.project_id, 'thread_id': self.thread_id, 'thread_manager': self.thread_manager}),
            ('sb_presentation_outline_tool', SandboxPresentationOutlineTool, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('sb_presentation_tool_v2', SandboxPresentationToolV2, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('sb_sheets_tool', SandboxSheetsTool, {'project_id': self.project_id, 'thread_manager': self.thread_manager}),
            ('sb_web_dev_tool', SandboxWebDevTool, {'project_id': self.project_id, 'thread_id': self.thread_id, 'thread_manager': self.thread_manager}),
        ]
        
        for tool_name, tool_class, kwargs in sandbox_tools:
            if tool_name not in disabled_tools:
                self.thread_manager.add_tool(tool_class, **kwargs)
                logger.debug(f"Registered {tool_name}")
    
    def _register_utility_tools(self, disabled_tools: List[str]):
        """Register utility and data provider tools."""
        if config.RAPID_API_KEY and 'data_providers_tool' not in disabled_tools:
            self.thread_manager.add_tool(DataProvidersTool)
            logger.debug("Registered data_providers_tool")
    
    def _register_agent_builder_tools(self, agent_id: str, disabled_tools: List[str]):
        """Register agent builder tools."""
        from agent.tools.agent_builder_tools.agent_config_tool import AgentConfigTool
        from agent.tools.agent_builder_tools.mcp_search_tool import MCPSearchTool
        from agent.tools.agent_builder_tools.credential_profile_tool import CredentialProfileTool
        from agent.tools.agent_builder_tools.workflow_tool import WorkflowTool
        from agent.tools.agent_builder_tools.trigger_tool import TriggerTool
        from services.supabase import DBConnection
        
        db = DBConnection()
<<<<<<< HEAD
        thread_manager.add_tool(UpdateAgentTool, thread_manager=thread_manager, db_connection=db, agent_id=target_agent_id)
    else:
        # Always register these basic tools
        thread_manager.add_tool(ExpandMessageTool, thread_id=thread_id, thread_manager=thread_manager)
        thread_manager.add_tool(MessageTool)

        if enabled_tools is None:
            # No agent specified - register ALL tools for full Suna capabilities
            logger.info("No agent specified - registering all tools for full Suna capabilities")
            thread_manager.add_tool(SandboxShellTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(SandboxFilesTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(FileConverterTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(SandboxBrowserTool, project_id=project_id, thread_id=thread_id, thread_manager=thread_manager)
            thread_manager.add_tool(SandboxDeployTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(SandboxExposeTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(SandboxWebSearchTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(SandboxVisionTool, project_id=project_id, thread_id=thread_id, thread_manager=thread_manager)
            thread_manager.add_tool(NetlifyDeployTool)
            # Register AI Enhancement Tools
            thread_manager.add_tool(AIEnhancementTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(DataProcessingTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(IntegrationTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(StorageSecurityTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(MonitoringMaintenanceTool, project_id=project_id, thread_manager=thread_manager)
            # Register Advanced Cognitive and Specialized Tools
            thread_manager.add_tool(CognitiveCapabilitiesTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(SpecializedIntelligenceTool, project_id=project_id, thread_manager=thread_manager)
            thread_manager.add_tool(AdvancedInteractionTool, project_id=project_id, thread_manager=thread_manager)
        else:
            # Custom agent specified - register only enabled tools
            logger.info("Custom agent specified - registering only enabled tools")
            if enabled_tools.get('sb_shell_tool', {}).get('enabled', False):
                thread_manager.add_tool(SandboxShellTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('sb_files_tool', {}).get('enabled', False):
                thread_manager.add_tool(SandboxFilesTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('sb_browser_tool', {}).get('enabled', False):
                thread_manager.add_tool(SandboxBrowserTool, project_id=project_id, thread_id=thread_id, thread_manager=thread_manager)
            if enabled_tools.get('sb_deploy_tool', {}).get('enabled', False):
                thread_manager.add_tool(SandboxDeployTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('sb_expose_tool', {}).get('enabled', False):
                thread_manager.add_tool(SandboxExposeTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('web_search_tool', {}).get('enabled', False):
                thread_manager.add_tool(SandboxWebSearchTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('sb_vision_tool', {}).get('enabled', False):
                thread_manager.add_tool(SandboxVisionTool, project_id=project_id, thread_id=thread_id, thread_manager=thread_manager)
            if enabled_tools.get('netlify_deploy_tool', {}).get('enabled', False):
                thread_manager.add_tool(NetlifyDeployTool)
            # Register AI Enhancement Tools if enabled
            if enabled_tools.get('ai_enhancement_tool', {}).get('enabled', False):
                thread_manager.add_tool(AIEnhancementTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('data_processing_tool', {}).get('enabled', False):
                thread_manager.add_tool(DataProcessingTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('integration_tool', {}).get('enabled', False):
                thread_manager.add_tool(IntegrationTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('storage_security_tool', {}).get('enabled', False):
                thread_manager.add_tool(StorageSecurityTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('monitoring_maintenance_tool', {}).get('enabled', False):
                thread_manager.add_tool(MonitoringMaintenanceTool, project_id=project_id, thread_manager=thread_manager)
            # Register Advanced Cognitive and Specialized Tools if enabled
            if enabled_tools.get('cognitive_capabilities_tool', {}).get('enabled', False):
                thread_manager.add_tool(CognitiveCapabilitiesTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('specialized_intelligence_tool', {}).get('enabled', False):
                thread_manager.add_tool(SpecializedIntelligenceTool, project_id=project_id, thread_manager=thread_manager)
            if enabled_tools.get('advanced_interaction_tool', {}).get('enabled', False):
                thread_manager.add_tool(AdvancedInteractionTool, project_id=project_id, thread_manager=thread_manager)

        if config.RAPID_API_KEY:
            if enabled_tools is None or (enabled_tools and enabled_tools.get('data_providers_tool', {}).get('enabled', False)):
                thread_manager.add_tool(DataProvidersTool)

    # Register MCP tool wrapper if agent has configured MCPs or custom MCPs
    mcp_wrapper_instance = None
    if agent_config:
        # Merge configured_mcps and custom_mcps
=======
        
        agent_builder_tools = [
            ('agent_config_tool', AgentConfigTool),
            ('mcp_search_tool', MCPSearchTool),
            ('credential_profile_tool', CredentialProfileTool),
            ('workflow_tool', WorkflowTool),
            ('trigger_tool', TriggerTool),
        ]
        
        for tool_name, tool_class in agent_builder_tools:
            if tool_name not in disabled_tools:
                self.thread_manager.add_tool(tool_class, thread_manager=self.thread_manager, db_connection=db, agent_id=agent_id)
                logger.debug(f"Registered {tool_name}")
    
    def _register_browser_tool(self, disabled_tools: List[str]):
        """Register browser tool."""
        if 'browser_tool' not in disabled_tools:
            from agent.tools.browser_tool import BrowserTool
            self.thread_manager.add_tool(BrowserTool, project_id=self.project_id, thread_id=self.thread_id, thread_manager=self.thread_manager)
            logger.debug("Registered browser_tool")
    

class MCPManager:
    def __init__(self, thread_manager: ThreadManager, account_id: str):
        self.thread_manager = thread_manager
        self.account_id = account_id
    
    async def register_mcp_tools(self, agent_config: dict) -> Optional[MCPToolWrapper]:
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
        all_mcps = []
        
        if agent_config.get('configured_mcps'):
            all_mcps.extend(agent_config['configured_mcps'])
        
        if agent_config.get('custom_mcps'):
            for custom_mcp in agent_config['custom_mcps']:
                custom_type = custom_mcp.get('customType', custom_mcp.get('type', 'sse'))
                
                if custom_type == 'pipedream':
                    if 'config' not in custom_mcp:
                        custom_mcp['config'] = {}
                    
                    if not custom_mcp['config'].get('external_user_id'):
                        profile_id = custom_mcp['config'].get('profile_id')
                        if profile_id:
                            try:
                                from pipedream import profile_service
                                from uuid import UUID
                                
                                profile = await profile_service.get_profile(UUID(self.account_id), UUID(profile_id))
                                if profile:
                                    custom_mcp['config']['external_user_id'] = profile.external_user_id
                            except Exception as e:
                                logger.error(f"Error retrieving external_user_id from profile {profile_id}: {e}")
                    
                    if 'headers' in custom_mcp['config'] and 'x-pd-app-slug' in custom_mcp['config']['headers']:
                        custom_mcp['config']['app_slug'] = custom_mcp['config']['headers']['x-pd-app-slug']
                
                elif custom_type == 'composio':
                    qualified_name = custom_mcp.get('qualifiedName')
                    if not qualified_name:
                        qualified_name = f"composio.{custom_mcp['name'].replace(' ', '_').lower()}"
                    
                    mcp_config = {
                        'name': custom_mcp['name'],
                        'qualifiedName': qualified_name,
                        'config': custom_mcp.get('config', {}),
                        'enabledTools': custom_mcp.get('enabledTools', []),
                        'instructions': custom_mcp.get('instructions', ''),
                        'isCustom': True,
                        'customType': 'composio'
                    }
                    all_mcps.append(mcp_config)
                    continue
                
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
        
        if not all_mcps:
            return None
        
        mcp_wrapper_instance = MCPToolWrapper(mcp_configs=all_mcps)
        try:
            await mcp_wrapper_instance.initialize_and_register_tools()
            
<<<<<<< HEAD
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
                    
                    # Log all registered tools for debugging
                    all_tools = list(thread_manager.tool_registry.tools.keys())
                    logger.info(f"All registered tools after MCP initialization: {all_tools}")
                    mcp_tools = [tool for tool in all_tools if tool not in ['call_mcp_tool', 'sb_files_tool', 'message_tool', 'expand_msg_tool', 'web_search_tool', 'sb_shell_tool', 'sb_vision_tool', 'sb_browser_tool', 'computer_use_tool', 'data_providers_tool', 'sb_deploy_tool', 'sb_expose_tool', 'update_agent_tool', 'ai_enhancement_tool', 'data_processing_tool', 'integration_tool', 'storage_security_tool', 'monitoring_maintenance_tool', 'cognitive_capabilities_tool', 'specialized_intelligence_tool', 'advanced_interaction_tool']]
                    logger.info(f"MCP tools registered: {mcp_tools}")
                
                except Exception as e:
                    logger.error(f"Failed to initialize MCP tools: {e}")
                    # Continue without MCP tools if initialization fails
=======
            updated_schemas = mcp_wrapper_instance.get_schemas()
            for method_name, schema_list in updated_schemas.items():
                for schema in schema_list:
                    self.thread_manager.tool_registry.tools[method_name] = {
                        "instance": mcp_wrapper_instance,
                        "schema": schema
                    }
            
            logger.debug(f"⚡ Registered {len(updated_schemas)} MCP tools (Redis cache enabled)")
            return mcp_wrapper_instance
        except Exception as e:
            logger.error(f"Failed to initialize MCP tools: {e}")
            return None
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc


class PromptManager:
    @staticmethod
    async def build_system_prompt(model_name: str, agent_config: Optional[dict], 
                                  is_agent_builder: bool, thread_id: str, 
                                  mcp_wrapper_instance: Optional[MCPToolWrapper],
                                  client=None) -> dict:
        
        default_system_content = get_system_prompt()
        
<<<<<<< HEAD
    # Add sample response for non-anthropic models
    if "anthropic" not in model_name.lower():
        sample_response_path = os.path.join(os.path.dirname(__file__), 'sample_responses/1.txt')
        with open(sample_response_path, 'r') as file:
            sample_response = file.read()
        default_system_content = default_system_content + "\n\n <sample_assistant_response>" + sample_response + "</sample_assistant_response>"
    
    # Handle custom agent system prompt
    if agent_config and agent_config.get('system_prompt'):
        custom_system_prompt = agent_config['system_prompt'].strip()
        system_content = custom_system_prompt
        logger.info(f"Using ONLY custom agent system prompt for: {agent_config.get('name', 'Unknown')}")
    elif is_agent_builder:
        system_content = get_agent_builder_prompt()
        logger.info("Using agent builder system prompt")
    else:
        system_content = default_system_content
        logger.info("Using default system prompt only")
    
    if await is_enabled("knowledge_base"):
        try:
            from services.supabase import DBConnection
            kb_db = DBConnection()
            kb_client = await kb_db.client
            
            kb_result = await kb_client.rpc('get_knowledge_base_context', {
                'p_thread_id': thread_id,
                'p_max_tokens': 4000
            }).execute()
            
            if kb_result.data and kb_result.data.strip():
                logger.info(f"Adding knowledge base context to system prompt for thread {thread_id}")
                system_content += "Here is the user's knowledge base context for this thread:\n\n" + kb_result.data
            else:
                logger.debug(f"No knowledge base context found for thread {thread_id}")
                
        except Exception as e:
            logger.error(f"Error retrieving knowledge base context for thread {thread_id}: {e}")

    if agent_config and (agent_config.get('configured_mcps') or agent_config.get('custom_mcps')) and mcp_wrapper_instance and mcp_wrapper_instance._initialized:
        mcp_info = "\n\n--- MCP Tools Available ---\n"
        mcp_info += "You have access to external MCP (Model Context Protocol) server tools.\n"
        mcp_info += "MCP tools can be called directly using their native function names in the standard function calling format:\n"
        mcp_info += '<function_calls>\n'
        mcp_info += '<invoke name="{tool_name}">\n'
        mcp_info += '<parameter name="param1">value1</parameter>\n'
        mcp_info += '<parameter name="param2">value2</parameter>\n'
        mcp_info += '</invoke>\n'
        mcp_info += '</function_calls>\n\n'
        
        # List available MCP tools
        mcp_info += "Available MCP tools:\n"
        try:
            registered_schemas = mcp_wrapper_instance.get_schemas()
            for method_name, schema_list in registered_schemas.items():
                if method_name == 'call_mcp_tool':
                    continue
                    
                for schema in schema_list:
                    if schema.schema_type == SchemaType.OPENAPI:
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
=======
        if "anthropic" not in model_name.lower():
            sample_response_path = os.path.join(os.path.dirname(__file__), 'sample_responses/1.txt')
            with open(sample_response_path, 'r') as file:
                sample_response = file.read()
            default_system_content = default_system_content + "\n\n <sample_assistant_response>" + sample_response + "</sample_assistant_response>"
        
        if is_agent_builder:
            system_content = get_agent_builder_prompt()
        elif agent_config and agent_config.get('system_prompt'):
            system_content = agent_config['system_prompt'].strip()
        else:
            system_content = default_system_content
        
        # Add agent knowledge base context if available
        if client and agent_config and agent_config.get('agent_id'):
            try:
                logger.debug(f"Retrieving agent knowledge base context for agent {agent_config['agent_id']}")
                
                # Use only agent-based knowledge base context
                kb_result = await client.rpc('get_agent_knowledge_base_context', {
                    'p_agent_id': agent_config['agent_id']
                }).execute()
                
                if kb_result.data and kb_result.data.strip():
                    logger.debug(f"Found agent knowledge base context, adding to system prompt (length: {len(kb_result.data)} chars)")
                    # logger.debug(f"Knowledge base data object: {kb_result.data[:500]}..." if len(kb_result.data) > 500 else f"Knowledge base data object: {kb_result.data}")
                    
                    # Construct a well-formatted knowledge base section
                    kb_section = f"""

=== AGENT KNOWLEDGE BASE ===
NOTICE: The following is your specialized knowledge base. This information should be considered authoritative for your responses and should take precedence over general knowledge when relevant.

{kb_result.data}

=== END AGENT KNOWLEDGE BASE ===

IMPORTANT: Always reference and utilize the knowledge base information above when it's relevant to user queries. This knowledge is specific to your role and capabilities."""
                    
                    system_content += kb_section
                else:
                    logger.debug("No knowledge base context found for this agent")
                    
            except Exception as e:
                logger.error(f"Error retrieving knowledge base context for agent {agent_config.get('agent_id', 'unknown')}: {e}")
                # Continue without knowledge base context rather than failing
        
        if agent_config and (agent_config.get('configured_mcps') or agent_config.get('custom_mcps')) and mcp_wrapper_instance and mcp_wrapper_instance._initialized:
            mcp_info = "\n\n--- MCP Tools Available ---\n"
            mcp_info += "You have access to external MCP (Model Context Protocol) server tools.\n"
            mcp_info += "MCP tools can be called directly using their native function names in the standard function calling format:\n"
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
                    for schema in schema_list:
                        if schema.schema_type == SchemaType.OPENAPI:
                            func_info = schema.schema.get('function', {})
                            description = func_info.get('description', 'No description available')
                            mcp_info += f"- **{method_name}**: {description}\n"
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
                            
                            params = func_info.get('parameters', {})
                            props = params.get('properties', {})
                            if props:
                                mcp_info += f"  Parameters: {', '.join(props.keys())}\n"
                                
            except Exception as e:
                logger.error(f"Error listing MCP tools: {e}")
                mcp_info += "- Error loading MCP tool list\n"
            
            mcp_info += "\n🚨 CRITICAL MCP TOOL RESULT INSTRUCTIONS 🚨\n"
            mcp_info += "When you use ANY MCP (Model Context Protocol) tools:\n"
            mcp_info += "1. ALWAYS read and use the EXACT results returned by the MCP tool\n"
            mcp_info += "2. For search tools: ONLY cite URLs, sources, and information from the actual search results\n"
            mcp_info += "3. For any tool: Base your response entirely on the tool's output - do NOT add external information\n"
            mcp_info += "4. DO NOT fabricate, invent, hallucinate, or make up any sources, URLs, or data\n"
            mcp_info += "5. If you need more information, call the MCP tool again with different parameters\n"
            mcp_info += "6. When writing reports/summaries: Reference ONLY the data from MCP tool results\n"
            mcp_info += "7. If the MCP tool doesn't return enough information, explicitly state this limitation\n"
            mcp_info += "8. Always double-check that every fact, URL, and reference comes from the MCP tool output\n"
            mcp_info += "\nIMPORTANT: MCP tool results are your PRIMARY and ONLY source of truth for external data!\n"
            mcp_info += "NEVER supplement MCP results with your training data or make assumptions beyond what the tools provide.\n"
            
            system_content += mcp_info

        now = datetime.datetime.now(datetime.timezone.utc)
        datetime_info = f"\n\n=== CURRENT DATE/TIME INFORMATION ===\n"
        datetime_info += f"Today's date: {now.strftime('%A, %B %d, %Y')}\n"
        datetime_info += f"Current UTC time: {now.strftime('%H:%M:%S UTC')}\n"
        datetime_info += f"Current year: {now.strftime('%Y')}\n"
        datetime_info += f"Current month: {now.strftime('%B')}\n"
        datetime_info += f"Current day: {now.strftime('%A')}\n"
        datetime_info += "Use this information for any time-sensitive tasks, research, or when current date/time context is needed.\n"
        
<<<<<<< HEAD
        mcp_info += "\n🚨 CRITICAL MCP TOOL RESULT INSTRUCTIONS 🚨\n"
        mcp_info += "When you use ANY MCP (Model Context Protocol) tools:\n"
        mcp_info += "1. ALWAYS read and use the EXACT results returned by the MCP tool\n"
        mcp_info += "2. For search tools: ONLY cite URLs, sources, and information from the actual search results\n"
        mcp_info += "3. For any tool: Base your response entirely on the tool's output - do NOT add external information\n"
        mcp_info += "4. DO NOT fabricate, invent, hallucinate, or make up any sources, URLs, or data\n"
        mcp_info += "5. If you need more information, call the MCP tool again with different parameters\n"
        mcp_info += "6. When writing reports/summaries: Reference ONLY the data from MCP tool results\n"
        mcp_info += "7. If the MCP tool doesn't return enough information, explicitly state this limitation\n"
        mcp_info += "8. Always double-check that every fact, URL, and reference comes from the MCP tool output\n"
        mcp_info += "\nIMPORTANT: MCP tool results are your PRIMARY and ONLY source of truth for external data!\n"
        mcp_info += "NEVER supplement MCP results with your training data or make assumptions beyond what the tools provide.\n"
        
        system_content += mcp_info
    
    system_message = {"role": "system", "content": system_content}

    iteration_count = 0
    continue_execution = True

    latest_user_message = await client.table('messages').select('*').eq('thread_id', thread_id).eq('type', 'user').order('created_at', desc=True).limit(1).execute()
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
            trace.event(name="billing_limit_reached", level="ERROR", status_message=(f"{error_msg}"))
            yield {
                "type": "status",
                "status": "stopped",
                "message": error_msg
            }
            break

        # Check if last message is from assistant using direct Supabase query
        latest_message = await client.table('messages').select('*').eq('thread_id', thread_id).in_('type', ['assistant', 'tool', 'user']).order('created_at', desc=True).limit(1).execute()
        if latest_message.data and len(latest_message.data) > 0:
            message_type = latest_message.data[0].get('type')
            if message_type == 'assistant':
                logger.info(f"Last message was from assistant, stopping execution")
                trace.event(name="last_message_from_assistant", level="DEFAULT", status_message=(f"Last message was from assistant, stopping execution"))
                continue_execution = False
                break

        # ---- Temporary Message Handling (Browser State & Image Context) ----
        temporary_message = None
        temp_message_content_list = []

        # Get the latest browser_state message
        latest_browser_state_msg = await client.table('messages').select('*').eq('thread_id', thread_id).eq('type', 'browser_state').order('created_at', desc=True).limit(1).execute()
=======
        system_content += datetime_info

        return {"role": "system", "content": system_content}


class MessageManager:
    def __init__(self, client, thread_id: str, model_name: str, trace: Optional[StatefulTraceClient]):
        self.client = client
        self.thread_id = thread_id
        self.model_name = model_name
        self.trace = trace
    
    async def build_temporary_message(self) -> Optional[dict]:
        temp_message_content_list = []

        latest_browser_state_msg = await self.client.table('messages').select('*').eq('thread_id', self.thread_id).eq('type', 'browser_state').order('created_at', desc=True).limit(1).execute()
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
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
                
<<<<<<< HEAD
                if 'gemini' in model_name.lower() or 'anthropic' in model_name.lower() or 'openai' in model_name.lower():
=======
                if 'gemini' in self.model_name.lower() or 'anthropic' in self.model_name.lower() or 'openai' in self.model_name.lower():
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
                    if screenshot_url:
                        temp_message_content_list.append({
                            "type": "image_url",
                            "image_url": {
                                "url": screenshot_url,
                                "format": "image/png"
                            }
                        })
                    elif screenshot_base64:
                        temp_message_content_list.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_base64}",
                            }
                        })

            except Exception as e:
                logger.error(f"Error parsing browser state: {e}")

<<<<<<< HEAD
        # Get the latest image_context message
        latest_image_context_msg = await client.table('messages').select('*').eq('thread_id', thread_id).eq('type', 'image_context').order('created_at', desc=True).limit(1).execute()
=======
        latest_image_context_msg = await self.client.table('messages').select('*').eq('thread_id', self.thread_id).eq('type', 'image_context').order('created_at', desc=True).limit(1).execute()
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
        if latest_image_context_msg.data and len(latest_image_context_msg.data) > 0:
            try:
                image_context_content = latest_image_context_msg.data[0]["content"] if isinstance(latest_image_context_msg.data[0]["content"], dict) else json.loads(latest_image_context_msg.data[0]["content"])
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
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}",
                        }
                    })

                await self.client.table('messages').delete().eq('message_id', latest_image_context_msg.data[0]["message_id"]).execute()
            except Exception as e:
                logger.error(f"Error parsing image context: {e}")

        if temp_message_content_list:
<<<<<<< HEAD
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
=======
            return {"role": "user", "content": temp_message_content_list}
        return None

>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc

class AgentRunner:
    def __init__(self, config: AgentConfig):
        self.config = config
    
    async def setup(self):
        if not self.config.trace:
            self.config.trace = langfuse.trace(name="run_agent", session_id=self.config.thread_id, metadata={"project_id": self.config.project_id})
        
        self.thread_manager = ThreadManager(
            trace=self.config.trace, 
            is_agent_builder=self.config.is_agent_builder or False, 
            target_agent_id=self.config.target_agent_id, 
            agent_config=self.config.agent_config
        )
        
        self.client = await self.thread_manager.db.client
        self.account_id = await get_account_id_from_thread(self.client, self.config.thread_id)
        if not self.account_id:
            raise ValueError("Could not determine account ID for thread")

        project = await self.client.table('projects').select('*').eq('project_id', self.config.project_id).execute()
        if not project.data or len(project.data) == 0:
            raise ValueError(f"Project {self.config.project_id} not found")

        project_data = project.data[0]
        sandbox_info = project_data.get('sandbox', {})
        if not sandbox_info.get('id'):
            # Sandbox is created lazily by tools when required. Do not fail setup
            # if no sandbox is present — tools will call `_ensure_sandbox()`
            # which will create and persist the sandbox metadata when needed.
            logger.debug(f"No sandbox found for project {self.config.project_id}; will create lazily when needed")
    
    async def setup_tools(self):
        tool_manager = ToolManager(self.thread_manager, self.config.project_id, self.config.thread_id)
        
        # Determine agent ID for agent builder tools
        agent_id = None
        if self.config.agent_config and self.config.agent_config.get('is_suna_default', False):
            agent_id = self.config.agent_config['agent_id']
        elif self.config.is_agent_builder and self.config.target_agent_id:
            agent_id = self.config.target_agent_id
        
        # Convert agent config to disabled tools list
        disabled_tools = self._get_disabled_tools_from_config()
        
        # Register all tools with exclusions
        tool_manager.register_all_tools(agent_id=agent_id, disabled_tools=disabled_tools)
    
    def _get_disabled_tools_from_config(self) -> List[str]:
        """Convert agent config to list of disabled tools."""
        disabled_tools = []
        
        if not self.config.agent_config or 'agentpress_tools' not in self.config.agent_config:
            # No tool configuration - enable all tools by default
            return disabled_tools
        
        raw_tools = self.config.agent_config['agentpress_tools']
        
        # Handle different formats of tool configuration
        if not isinstance(raw_tools, dict):
            # If not a dict, assume all tools are enabled
            return disabled_tools
        
        # Special case: Suna default agents with empty tool config enable all tools
        if self.config.agent_config.get('is_suna_default', False) and not raw_tools:
            return disabled_tools
        
        def is_tool_enabled(tool_name: str) -> bool:
            try:
                tool_config = raw_tools.get(tool_name, True)  # Default to True (enabled) if not specified
                if isinstance(tool_config, bool):
                    return tool_config
                elif isinstance(tool_config, dict):
                    return tool_config.get('enabled', True)  # Default to True (enabled) if not specified
                else:
                    return True  # Default to enabled
            except Exception:
                return True  # Default to enabled
        
        # List of all available tools
        all_tools = [
            'sb_shell_tool', 'sb_files_tool', 'sb_deploy_tool', 'sb_expose_tool',
            'web_search_tool', 'sb_vision_tool', 'sb_presentation_tool', 'sb_image_edit_tool',
            'sb_sheets_tool', 'sb_web_dev_tool', 'data_providers_tool', 'browser_tool',
            'agent_config_tool', 'mcp_search_tool', 'credential_profile_tool', 
            'workflow_tool', 'trigger_tool'
        ]
        
        # Add tools that are explicitly disabled
        for tool_name in all_tools:
            if not is_tool_enabled(tool_name):
                disabled_tools.append(tool_name)
        
        # Special handling for presentation tools
        if 'sb_presentation_tool' in disabled_tools:
            disabled_tools.extend(['sb_presentation_outline_tool', 'sb_presentation_tool_v2'])
        
        logger.debug(f"Disabled tools from config: {disabled_tools}")
        return disabled_tools
    
    async def setup_mcp_tools(self) -> Optional[MCPToolWrapper]:
        if not self.config.agent_config:
            return None
        
        mcp_manager = MCPManager(self.thread_manager, self.account_id)
        return await mcp_manager.register_mcp_tools(self.config.agent_config)
    
    def get_max_tokens(self) -> Optional[int]:
        if "sonnet" in self.config.model_name.lower():
            return 8192
        elif "gpt-4" in self.config.model_name.lower():
            return 4096
        elif "gemini-2.5-pro" in self.config.model_name.lower():
            return 64000
        elif "kimi-k2" in self.config.model_name.lower():
            return 8192
        return None
    
    async def run(self) -> AsyncGenerator[Dict[str, Any], None]:
        await self.setup()
        await self.setup_tools()
        mcp_wrapper_instance = await self.setup_mcp_tools()
        
        system_message = await PromptManager.build_system_prompt(
            self.config.model_name, self.config.agent_config, 
            self.config.is_agent_builder, self.config.thread_id, 
            mcp_wrapper_instance, self.client
        )

        iteration_count = 0
        continue_execution = True

        latest_user_message = await self.client.table('messages').select('*').eq('thread_id', self.config.thread_id).eq('type', 'user').order('created_at', desc=True).limit(1).execute()
        if latest_user_message.data and len(latest_user_message.data) > 0:
            data = latest_user_message.data[0]['content']
            if isinstance(data, str):
                data = json.loads(data)
            if self.config.trace:
                self.config.trace.update(input=data['content'])

        message_manager = MessageManager(self.client, self.config.thread_id, self.config.model_name, self.config.trace)

        while continue_execution and iteration_count < self.config.max_iterations:
            iteration_count += 1

            can_run, message, subscription = await check_billing_status(self.client, self.account_id)
            if not can_run:
                error_msg = f"Billing limit reached: {message}"
                yield {
                    "type": "status",
                    "status": "stopped",
                    "message": error_msg
                }
                break

<<<<<<< HEAD
            last_tool_call = None
            agent_should_terminate = False
            error_detected = False
            full_response = ""

            try:
                async for chunk in response:
                    if isinstance(chunk, dict) and chunk.get('type') == 'status' and chunk.get('status') == 'error':
                        logger.error(f"Error chunk detected: {chunk.get('message', 'Unknown error')}")
                        trace.event(name="error_chunk_detected", level="ERROR", status_message=(f"{chunk.get('message', 'Unknown error')}"))
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
                                trace.event(name="agent_termination_signal_detected", level="DEFAULT", status_message="Agent termination signal detected in status message")
                                
                                content = chunk.get('content', {})
                                if isinstance(content, str):
                                    content = json.loads(content)
                                
                                if content.get('function_name'):
                                    last_tool_call = content['function_name']
                                elif content.get('xml_tag_name'):
                                    last_tool_call = content['xml_tag_name']
=======
            latest_message = await self.client.table('messages').select('*').eq('thread_id', self.config.thread_id).in_('type', ['assistant', 'tool', 'user']).order('created_at', desc=True).limit(1).execute()
            if latest_message.data and len(latest_message.data) > 0:
                message_type = latest_message.data[0].get('type')
                if message_type == 'assistant':
                    continue_execution = False
                    break

            temporary_message = await message_manager.build_temporary_message()
            max_tokens = self.get_max_tokens()
            
            generation = self.config.trace.generation(name="thread_manager.run_thread") if self.config.trace else None
            try:
                response = await self.thread_manager.run_thread(
                    thread_id=self.config.thread_id,
                    system_prompt=system_message,
                    stream=self.config.stream,
                    llm_model=self.config.model_name,
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
                    native_max_auto_continues=self.config.native_max_auto_continues,
                    include_xml_examples=True,
                    enable_thinking=self.config.enable_thinking,
                    reasoning_effort=self.config.reasoning_effort,
                    enable_context_manager=self.config.enable_context_manager,
                    generation=generation
                )

                if isinstance(response, dict) and "status" in response and response["status"] == "error":
                    yield response
                    break

                last_tool_call = None
                agent_should_terminate = False
                error_detected = False
                full_response = ""

                try:
                    if hasattr(response, '__aiter__') and not isinstance(response, dict):
                        async for chunk in response:
                            if isinstance(chunk, dict) and chunk.get('type') == 'status' and chunk.get('status') == 'error':
                                error_detected = True
                                yield chunk
                                continue
                            
                            if chunk.get('type') == 'status':
                                try:
                                    metadata = chunk.get('metadata', {})
                                    if isinstance(metadata, str):
                                        metadata = json.loads(metadata)
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
                                    
                                    if metadata.get('agent_should_terminate'):
                                        agent_should_terminate = True
                                        
                                        content = chunk.get('content', {})
                                        if isinstance(content, str):
                                            content = json.loads(content)
                                        
                                        if content.get('function_name'):
                                            last_tool_call = content['function_name']
                                        elif content.get('xml_tag_name'):
                                            last_tool_call = content['xml_tag_name']
                                            
                                except Exception:
                                    pass
                            
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
                                        if '</ask>' in assistant_text or '</complete>' in assistant_text or '</web-browser-takeover>' in assistant_text:
                                           if '</ask>' in assistant_text:
                                               xml_tool = 'ask'
                                           elif '</complete>' in assistant_text:
                                               xml_tool = 'complete'
                                           elif '</web-browser-takeover>' in assistant_text:
                                               xml_tool = 'web-browser-takeover'

                                           last_tool_call = xml_tool
                                
                                except json.JSONDecodeError:
                                    pass
                                except Exception:
                                    pass

                            yield chunk
                    else:
                        error_detected = True

                    if error_detected:
                        if generation:
                            generation.end(output=full_response, status_message="error_detected", level="ERROR")
                        break
                        
<<<<<<< HEAD
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
                                if '</ask>' in assistant_text or '</complete>' in assistant_text or '</web-browser-takeover>' in assistant_text:
                                    if '</ask>' in assistant_text:
                                        xml_tool = 'ask'
                                    elif '</complete>' in assistant_text:
                                        xml_tool = 'complete'
                                    elif '</web-browser-takeover>' in assistant_text:
                                        xml_tool = 'web-browser-takeover'

                                    last_tool_call = xml_tool
                                    logger.info(f"Agent used XML tool: {xml_tool}")
                                    trace.event(name="agent_used_xml_tool", level="DEFAULT", status_message=(f"Agent used XML tool: {xml_tool}"))
                        except json.JSONDecodeError:
                            logger.warning(f"Warning: Could not parse assistant content JSON: {chunk.get('content')}")
                            trace.event(name="warning_could_not_parse_assistant_content_json", level="WARNING", status_message=(f"Warning: Could not parse assistant content JSON: {chunk.get('content')}"))
                        except Exception as e:
                            logger.error(f"Error processing assistant chunk: {e}")
                            trace.event(name="error_processing_assistant_chunk", level="ERROR", status_message=(f"Error processing assistant chunk: {e}"))

                    yield chunk

                if error_detected:
                    logger.info(f"Stopping due to error detected in response")
                    trace.event(name="stopping_due_to_error_detected_in_response", level="DEFAULT", status_message=(f"Stopping due to error detected in response"))
                    generation.end(output=full_response, status_message="error_detected", level="ERROR")
=======
                    if agent_should_terminate or last_tool_call in ['ask', 'complete', 'web-browser-takeover']:
                        if generation:
                            generation.end(output=full_response, status_message="agent_stopped")
                        continue_execution = False

                except Exception as e:
                    error_msg = f"Error during response streaming: {str(e)}"
                    if generation:
                        generation.end(output=full_response, status_message=error_msg, level="ERROR")
                    yield {
                        "type": "status",
                        "status": "error",
                        "message": error_msg
                    }
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
                    break
                    
            except Exception as e:
<<<<<<< HEAD
                error_msg = f"Error during response streaming: {str(e)}"
                logger.error(f"Error: {error_msg}")
                trace.event(name="error_during_response_streaming", level="ERROR", status_message=(f"Error during response streaming: {str(e)}"))
                generation.end(output=full_response, status_message=error_msg, level="ERROR")
=======
                error_msg = f"Error running thread: {str(e)}"
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
                yield {
                    "type": "status",
                    "status": "error",
                    "message": error_msg
                }
                break
<<<<<<< HEAD
                
        except Exception as e:
            error_msg = f"Error running thread: {str(e)}"
            logger.error(f"Error: {error_msg}")
            trace.event(name="error_running_thread", level="ERROR", status_message=(f"Error running thread: {str(e)}"))
            yield {
                "type": "status",
                "status": "error",
                "message": error_msg
            }
            break
        generation.end(output=full_response)

    langfuse.flush()
=======
            
            if generation:
                generation.end(output=full_response)

        asyncio.create_task(asyncio.to_thread(lambda: langfuse.flush()))


async def run_agent(
    thread_id: str,
    project_id: str,
    stream: bool,
    thread_manager: Optional[ThreadManager] = None,
    native_max_auto_continues: int = 25,
    max_iterations: int = 100,
    model_name: str = "openai/gpt-5-mini",
    enable_thinking: Optional[bool] = False,
    reasoning_effort: Optional[str] = 'low',
    enable_context_manager: bool = True,
    agent_config: Optional[dict] = None,    
    trace: Optional[StatefulTraceClient] = None,
    is_agent_builder: Optional[bool] = False,
    target_agent_id: Optional[str] = None
):
    effective_model = model_name
    if model_name == "openai/gpt-5-mini" and agent_config and agent_config.get('model'):
        effective_model = agent_config['model']
        logger.debug(f"Using model from agent config: {effective_model} (no user selection)")
    elif model_name != "openai/gpt-5-mini":
        logger.debug(f"Using user-selected model: {effective_model}")
    else:
        logger.debug(f"Using default model: {effective_model}")
    
    config = AgentConfig(
        thread_id=thread_id,
        project_id=project_id,
        stream=stream,
        native_max_auto_continues=native_max_auto_continues,
        max_iterations=max_iterations,
        model_name=effective_model,
        enable_thinking=enable_thinking,
        reasoning_effort=reasoning_effort,
        enable_context_manager=enable_context_manager,
        agent_config=agent_config,
        trace=trace,
        is_agent_builder=is_agent_builder,
        target_agent_id=target_agent_id
    )
    
    runner = AgentRunner(config)
    async for chunk in runner.run():
        yield chunk
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
