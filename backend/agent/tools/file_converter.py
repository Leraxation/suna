from agentpress.tool import Tool, ToolResult, openapi_schema
# from ..sandbox_shell import SandboxShellTool  # Temporarily commented out due to missing file
import asyncio

class FileConverterTool(Tool):
    def __init__(self, agent_run):
        super().__init__(agent_run)
        # self.shell = SandboxShellTool(agent_run)  # Disabled due to missing dependency
        self.shell = None  # Placeholder to avoid runtime errors

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "convert_markdown_to_pdf",
            "description": "Converts a Markdown file to a PDF document using Pandoc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "markdown_file_path": {
                        "type": "string",
                        "description": "The path to the input Markdown (.md) file in the workspace."
                    },
                    "output_pdf_path": {
                        "type": "string",
                        "description": "The desired path for the output PDF (.pdf) file in the workspace."
                    }
                },
                "required": ["markdown_file_path", "output_pdf_path"]
            }
        }
    })
    async def convert_markdown_to_pdf(self, markdown_file_path: str, output_pdf_path: str) -> ToolResult:
        if self.shell is None:
            return self.fail_response("File conversion disabled due to missing sandbox shell dependency.")
        command = f"pandoc {markdown_file_path} -o {output_pdf_path}"
        result = await self.shell.execute_command(command, blocking=True)
        if "error" in result.output.lower() or "command not found" in result.output.lower():
            return self.fail_response(f"Error converting to PDF: {result.output}")
        return self.success_response(f"Successfully converted {markdown_file_path} to {output_pdf_path}.")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "convert_markdown_to_html",
            "description": "Converts a Markdown file to a standalone HTML document using Pandoc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "markdown_file_path": {
                        "type": "string",
                        "description": "The path to the input Markdown (.md) file in the workspace."
                    },
                    "output_html_path": {
                        "type": "string",
                        "description": "The desired path for the output HTML (.html) file in the workspace."
                    }
                },
                "required": ["markdown_file_path", "output_html_path"]
            }
        }
    })
    async def convert_markdown_to_html(self, markdown_file_path: str, output_html_path: str) -> ToolResult:
        if self.shell is None:
            return self.fail_response("File conversion disabled due to missing sandbox shell dependency.")
        command = f"pandoc {markdown_file_path} -s -o {output_html_path}"
        result = await self.shell.execute_command(command, blocking=True)
        if "error" in result.output.lower() or "command not found" in result.output.lower():
            return self.fail_response(f"Error converting to HTML: {result.output}")
        return self.success_response(f"Successfully converted {markdown_file_path} to {output_html_path}.")