import asyncio
import json
import logging
import os
import sys
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from dotenv import load_dotenv

from .config import AppSettings, settings as global_settings # Import AppSettings and the global instance
# Import from _internal
from ._internal.agent.browser_use.browser_use_agent import BrowserUseAgent, AgentHistoryList
from ._internal.agent.deep_research.deep_research_agent import DeepResearchAgent
from ._internal.browser.custom_browser import CustomBrowser
from ._internal.browser.custom_context import (
    CustomBrowserContext,
    CustomBrowserContextConfig,
)
from ._internal.controller.custom_controller import CustomController
from ._internal.utils import llm_provider as internal_llm_provider
from browser_use.browser.browser import BrowserConfig
from browser_use.agent.views import AgentOutput
from browser_use.browser.views import BrowserState

app = typer.Typer(name="mcp-browser-cli", help="CLI for mcp-browser-use tools.")
logger = logging.getLogger("mcp_browser_cli")

class CLIState:
    settings: Optional[AppSettings] = None

cli_state = CLIState()

def setup_logging(level_str: str, log_file: Optional[str]):
    numeric_level = getattr(logging, level_str.upper(), logging.INFO)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=log_file if log_file else None,
        filemode="a" if log_file else None,
        force=True
    )

@app.callback()
def main_callback(
    ctx: typer.Context,
    env_file: Optional[Path] = typer.Option(
        None, "--env-file", "-e", help="Path to .env file to load.", exists=True, dir_okay=False, resolve_path=True
    ),
    log_level: Optional[str] = typer.Option(
        None, "--log-level", "-l", help="Override logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."
    )
):
    """
    MCP Browser Use CLI. Settings are loaded from environment variables.
    You can use an .env file for convenience.
    """
    if env_file:
        load_dotenv(env_file, override=True)
        logger.info(f"Loaded environment variables from: {env_file}")

    # Reload settings after .env might have been loaded and to apply overrides
    try:
        cli_state.settings = AppSettings()
    except Exception as e:
        # This can happen if mandatory fields (like MCP_RESEARCH_TOOL_SAVE_DIR) are not set
        sys.stderr.write(f"Error loading application settings: {e}\n")
        sys.stderr.write("Please ensure all mandatory environment variables are set (e.g., MCP_RESEARCH_TOOL_SAVE_DIR).\n")
        raise typer.Exit(code=1)

    # Setup logging based on final settings (env file, then env vars, then CLI override)
    final_log_level = log_level if log_level else cli_state.settings.server.logging_level
    final_log_file = cli_state.settings.server.log_file
    setup_logging(final_log_level, final_log_file)

    logger.info(f"CLI initialized. Effective log level: {final_log_level.upper()}")
    if not cli_state.settings: # Should not happen if AppSettings() worked
        logger.error("Failed to load application settings.")
        raise typer.Exit(code=1)


async def cli_ask_human_callback(query: str, browser_context: Any) -> Dict[str, Any]:
    """Callback for agent to ask human for input via CLI."""
    # browser_context is part of the signature from browser-use, might not be needed here
    print(typer.style(f"\n🤖 AGENT ASKS: {query}", fg=typer.colors.YELLOW))
    response_text = typer.prompt(typer.style("Your response", fg=typer.colors.CYAN))
    return {"response": response_text}

def cli_on_step_callback(browser_state: BrowserState, agent_output: AgentOutput, step_num: int):
    """CLI callback for BrowserUseAgent steps."""
    print(typer.style(f"\n--- Step {step_num} ---", fg=typer.colors.BLUE, bold=True))
    # Print current state if available
    if hasattr(agent_output, "current_state") and agent_output.current_state:
        print(typer.style("🧠 Agent State:", fg=typer.colors.MAGENTA))
        print(agent_output.current_state)
    # Print actions
    if hasattr(agent_output, "action") and agent_output.action:
        print(typer.style("🎬 Actions:", fg=typer.colors.GREEN))
        for action in agent_output.action:
            # Try to get action_type and action_input if present, else print the action itself
            action_type = getattr(action, "action_type", None)
            action_input = getattr(action, "action_input", None)
            if action_type is not None or action_input is not None:
                print(f"  - {action_type or 'Unknown action'}: {action_input or ''}")
            else:
                print(f"  - {action}")
    # Optionally print observation if present in browser_state
    if hasattr(browser_state, "observation") and browser_state.observation:
        obs = browser_state.observation
        print(typer.style("👀 Observation:", fg=typer.colors.CYAN))
        print(str(obs)[:200] + "..." if obs and len(str(obs)) > 200 else obs)


async def _run_browser_agent_logic_cli(task_str: str, current_settings: AppSettings) -> str:
    logger.info(f"CLI: Starting run_browser_agent task: {task_str[:100]}...")
    agent_task_id = str(uuid.uuid4())
    final_result = "Error: Agent execution failed."

    browser_instance: Optional[CustomBrowser] = None
    context_instance: Optional[CustomBrowserContext] = None
    controller_instance: Optional[CustomController] = None

    try:
        # LLM Setup
        main_llm_config = current_settings.get_llm_config()
        main_llm = internal_llm_provider.get_llm_model(**main_llm_config)
        planner_llm = None
        if current_settings.llm.planner_provider and current_settings.llm.planner_model_name:
            planner_llm_config = current_settings.get_llm_config(is_planner=True)
            planner_llm = internal_llm_provider.get_llm_model(**planner_llm_config)

        # Controller Setup
        controller_instance = CustomController(ask_assistant_callback=cli_ask_human_callback)
        if current_settings.server.mcp_config:
            mcp_dict_config = current_settings.server.mcp_config
            if isinstance(current_settings.server.mcp_config, str):
                mcp_dict_config = json.loads(current_settings.server.mcp_config)
            await controller_instance.setup_mcp_client(mcp_dict_config)

        # Browser and Context Setup
        agent_headless_override = current_settings.agent_tool.headless
        browser_headless = agent_headless_override if agent_headless_override is not None else current_settings.browser.headless
        agent_disable_security_override = current_settings.agent_tool.disable_security
        browser_disable_security = agent_disable_security_override if agent_disable_security_override is not None else current_settings.browser.disable_security

        if current_settings.browser.use_own_browser and current_settings.browser.cdp_url:
            browser_cfg = BrowserConfig(cdp_url=current_settings.browser.cdp_url, wss_url=current_settings.browser.wss_url, user_data_dir=current_settings.browser.user_data_dir)
        else:
            browser_cfg = BrowserConfig(
                headless=browser_headless,
                disable_security=browser_disable_security,
                browser_binary_path=current_settings.browser.binary_path,
                user_data_dir=current_settings.browser.user_data_dir,
                window_width=current_settings.browser.window_width,
                window_height=current_settings.browser.window_height,
            )
        browser_instance = CustomBrowser(config=browser_cfg)

        context_cfg = CustomBrowserContextConfig(
            trace_path=current_settings.browser.trace_path,
            save_downloads_path=current_settings.paths.downloads,
            save_recording_path=current_settings.agent_tool.save_recording_path if current_settings.agent_tool.enable_recording else None,
            force_new_context=True # CLI always gets a new context
        )
        context_instance = await browser_instance.new_context(config=context_cfg)

        agent_history_json_file = None
        task_history_base_path = current_settings.agent_tool.history_path

        if task_history_base_path:
            task_specific_history_dir = Path(task_history_base_path) / agent_task_id
            task_specific_history_dir.mkdir(parents=True, exist_ok=True)
            agent_history_json_file = str(task_specific_history_dir / f"{agent_task_id}.json")
            logger.info(f"Agent history will be saved to: {agent_history_json_file}")

        # Agent Instantiation
        agent_instance = BrowserUseAgent(
            task=task_str, llm=main_llm,
            browser=browser_instance, browser_context=context_instance, controller=controller_instance,
            planner_llm=planner_llm,
            max_actions_per_step=current_settings.agent_tool.max_actions_per_step,
            use_vision=current_settings.agent_tool.use_vision,
            register_new_step_callback=cli_on_step_callback,
        )

        # Run Agent
        history: AgentHistoryList = await agent_instance.run(max_steps=current_settings.agent_tool.max_steps)
        agent_instance.save_history(agent_history_json_file)
        final_result = history.final_result() or "Agent finished without a final result."
        logger.info(f"CLI Agent task {agent_task_id} completed.")

    except Exception as e:
        logger.error(f"CLI Error in run_browser_agent: {e}\n{traceback.format_exc()}")
        final_result = f"Error: {e}"
    finally:
        if context_instance: await context_instance.close()
        if browser_instance and not current_settings.browser.use_own_browser : await browser_instance.close() # Only close if we launched it
        if controller_instance: await controller_instance.close_mcp_client()

    return final_result


async def _run_deep_research_logic_cli(research_task_str: str, max_parallel_browsers_override: Optional[int], current_settings: AppSettings) -> str:
    logger.info(f"CLI: Starting run_deep_research task: {research_task_str[:100]}...")
    task_id = str(uuid.uuid4())
    report_content = "Error: Deep research failed."

    try:
        main_llm_config = current_settings.get_llm_config()
        research_llm = internal_llm_provider.get_llm_model(**main_llm_config)

        dr_browser_cfg = {
            "headless": current_settings.browser.headless,
            "disable_security": current_settings.browser.disable_security,
            "browser_binary_path": current_settings.browser.binary_path,
            "user_data_dir": current_settings.browser.user_data_dir,
            "window_width": current_settings.browser.window_width,
            "window_height": current_settings.browser.window_height,
            "trace_path": current_settings.browser.trace_path,
            "save_downloads_path": current_settings.paths.downloads,
        }
        if current_settings.browser.use_own_browser and current_settings.browser.cdp_url:
            dr_browser_cfg["cdp_url"] = current_settings.browser.cdp_url
            dr_browser_cfg["wss_url"] = current_settings.browser.wss_url

        mcp_server_config_for_agent = None
        if current_settings.server.mcp_config:
            mcp_server_config_for_agent = current_settings.server.mcp_config
            if isinstance(current_settings.server.mcp_config, str):
                 mcp_server_config_for_agent = json.loads(current_settings.server.mcp_config)

        agent_instance = DeepResearchAgent(
            llm=research_llm, browser_config=dr_browser_cfg,
            mcp_server_config=mcp_server_config_for_agent,
        )

        current_max_parallel_browsers = max_parallel_browsers_override if max_parallel_browsers_override is not None else current_settings.research_tool.max_parallel_browsers

        save_dir_for_task = os.path.join(current_settings.research_tool.save_dir, task_id)
        os.makedirs(save_dir_for_task, exist_ok=True)

        logger.info(f"CLI Deep research save directory: {save_dir_for_task}")
        logger.info(f"CLI Using max_parallel_browsers: {current_max_parallel_browsers}")

        result_dict = await agent_instance.run(
            topic=research_task_str, task_id=task_id,
            save_dir=save_dir_for_task, max_parallel_browsers=current_max_parallel_browsers
        )

        report_file_path = result_dict.get("report_file_path")
        if report_file_path and os.path.exists(report_file_path):
            with open(report_file_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            report_content = f"Deep research report generated successfully at {report_file_path}\n\n{markdown_content}"
            logger.info(f"CLI Deep research task {task_id} completed. Report at {report_file_path}")
        else:
            report_content = f"Deep research completed, but report file not found. Result: {result_dict}"
            logger.warning(f"CLI Deep research task {task_id} result: {result_dict}, report file path missing or invalid.")

    except Exception as e:
        logger.error(f"CLI Error in run_deep_research: {e}\n{traceback.format_exc()}")
        report_content = f"Error: {e}"

    return report_content


@app.command()
def run_browser_agent(
    task: str = typer.Argument(..., help="The primary task or objective for the browser agent."),
):
    """Runs a browser agent task and prints the result."""
    if not cli_state.settings:
        typer.secho("Error: Application settings not loaded. Use --env-file or set environment variables.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Executing browser agent task: {task}", fg=typer.colors.GREEN)
    try:
        result = asyncio.run(_run_browser_agent_logic_cli(task, cli_state.settings))
        typer.secho("\n--- Agent Final Result ---", fg=typer.colors.BLUE, bold=True)
        print(result)
    except Exception as e:
        typer.secho(f"CLI command failed: {e}", fg=typer.colors.RED)
        logger.error(f"CLI run_browser_agent command failed: {e}\n{traceback.format_exc()}")
        raise typer.Exit(code=1)

@app.command()
def run_deep_research(
    research_task: str = typer.Argument(..., help="The topic or question for deep research."),
    max_parallel_browsers: Optional[int] = typer.Option(None, "--max-parallel-browsers", "-p", help="Override max parallel browsers from settings.")
):
    """Performs deep web research and prints the report."""
    if not cli_state.settings:
        typer.secho("Error: Application settings not loaded. Use --env-file or set environment variables.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Executing deep research task: {research_task}", fg=typer.colors.GREEN)
    try:
        result = asyncio.run(_run_deep_research_logic_cli(research_task, max_parallel_browsers, cli_state.settings))
        typer.secho("\n--- Deep Research Final Report ---", fg=typer.colors.BLUE, bold=True)
        print(result)
    except Exception as e:
        typer.secho(f"CLI command failed: {e}", fg=typer.colors.RED)
        logger.error(f"CLI run_deep_research command failed: {e}\n{traceback.format_exc()}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    # This allows running `python src/mcp_server_browser_use/cli.py ...`
    # Set a default log level if run directly for dev purposes, can be overridden by CLI args
    if not os.getenv("MCP_SERVER_LOGGING_LEVEL"): # Check if already set
        os.environ["MCP_SERVER_LOGGING_LEVEL"] = "DEBUG"
    if not os.getenv("MCP_RESEARCH_TOOL_SAVE_DIR"): # Ensure mandatory var is set for local dev
        print("Warning: MCP_RESEARCH_TOOL_SAVE_DIR not set. Defaulting to './tmp/deep_research_cli_default' for this run.", file=sys.stderr)
        os.environ["MCP_RESEARCH_TOOL_SAVE_DIR"] = "./tmp/deep_research_cli_default"

    app()
