from typing import Any, Dict, List, Optional, Union

from pydantic import Field, SecretStr, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_LLM_")

    provider: str = Field(default="google", env="PROVIDER")
    model_name: str = Field(default="gemini-2.5-flash-preview-04-17", env="MODEL_NAME")
    temperature: float = Field(default=0.0, env="TEMPERATURE")
    base_url: Optional[str] = Field(default=None, env="BASE_URL")
    api_key: Optional[SecretStr] = Field(default=None, env="API_KEY") # Generic API key

    # Provider-specific API keys
    openai_api_key: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[SecretStr] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[SecretStr] = Field(default=None, env="GOOGLE_API_KEY")
    azure_openai_api_key: Optional[SecretStr] = Field(default=None, env="AZURE_OPENAI_API_KEY")
    deepseek_api_key: Optional[SecretStr] = Field(default=None, env="DEEPSEEK_API_KEY")
    mistral_api_key: Optional[SecretStr] = Field(default=None, env="MISTRAL_API_KEY")
    openrouter_api_key: Optional[SecretStr] = Field(default=None, env="OPENROUTER_API_KEY")
    alibaba_api_key: Optional[SecretStr] = Field(default=None, env="ALIBABA_API_KEY")
    moonshot_api_key: Optional[SecretStr] = Field(default=None, env="MOONSHOT_API_KEY")
    unbound_api_key: Optional[SecretStr] = Field(default=None, env="UNBOUND_API_KEY")

    # Provider-specific endpoints
    openai_endpoint: Optional[str] = Field(default=None, env="OPENAI_ENDPOINT")
    anthropic_endpoint: Optional[str] = Field(default=None, env="ANTHROPIC_ENDPOINT")
    azure_openai_endpoint: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field(default="2025-01-01-preview", env="AZURE_OPENAI_API_VERSION")
    deepseek_endpoint: Optional[str] = Field(default=None, env="DEEPSEEK_ENDPOINT")
    mistral_endpoint: Optional[str] = Field(default=None, env="MISTRAL_ENDPOINT")
    ollama_endpoint: str = Field(default="http://localhost:11434", env="OLLAMA_ENDPOINT")
    openrouter_endpoint: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_ENDPOINT")
    alibaba_endpoint: Optional[str] = Field(default=None, env="ALIBABA_ENDPOINT")
    moonshot_endpoint: Optional[str] = Field(default=None, env="MOONSHOT_ENDPOINT")
    unbound_endpoint: Optional[str] = Field(default=None, env="UNBOUND_ENDPOINT")

    ollama_num_ctx: Optional[int] = Field(default=32000, env="OLLAMA_NUM_CTX")
    ollama_num_predict: Optional[int] = Field(default=1024, env="OLLAMA_NUM_PREDICT")

    # Planner LLM settings (optional, defaults to main LLM if not set)
    planner_provider: Optional[str] = Field(default=None, env="PLANNER_PROVIDER")
    planner_model_name: Optional[str] = Field(default=None, env="PLANNER_MODEL_NAME")
    planner_temperature: Optional[float] = Field(default=None, env="PLANNER_TEMPERATURE")
    planner_base_url: Optional[str] = Field(default=None, env="PLANNER_BASE_URL")
    planner_api_key: Optional[SecretStr] = Field(default=None, env="PLANNER_API_KEY")


class BrowserSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_BROWSER_")

    headless: bool = Field(default=False, env="HEADLESS") # General headless
    disable_security: bool = Field(default=False, env="DISABLE_SECURITY") # General disable security
    binary_path: Optional[str] = Field(default=None, env="BINARY_PATH")
    user_data_dir: Optional[str] = Field(default=None, env="USER_DATA_DIR")
    window_width: int = Field(default=1280, env="WINDOW_WIDTH")
    window_height: int = Field(default=1080, env="WINDOW_HEIGHT")
    use_own_browser: bool = Field(default=False, env="USE_OWN_BROWSER")
    cdp_url: Optional[str] = Field(default=None, env="CDP_URL")
    wss_url: Optional[str] = Field(default=None, env="WSS_URL") # For CDP connection if needed
    keep_open: bool = Field(default=False, env="KEEP_OPEN") # Server-managed browser persistence
    trace_path: Optional[str] = Field(default=None, env="TRACE_PATH")


class AgentToolSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_AGENT_TOOL_")

    max_steps: int = Field(default=100, env="MAX_STEPS")
    max_actions_per_step: int = Field(default=5, env="MAX_ACTIONS_PER_STEP")
    tool_calling_method: Optional[str] = Field(default="auto", env="TOOL_CALLING_METHOD")
    max_input_tokens: Optional[int] = Field(default=128000, env="MAX_INPUT_TOKENS")
    use_vision: bool = Field(default=True, env="USE_VISION")

    # Browser settings specific to this tool, can override general MCP_BROWSER_ settings
    headless: Optional[bool] = Field(default=None, env="HEADLESS")
    disable_security: Optional[bool] = Field(default=None, env="DISABLE_SECURITY")

    enable_recording: bool = Field(default=False, env="ENABLE_RECORDING")
    save_recording_path: Optional[str] = Field(default=None, env="SAVE_RECORDING_PATH") # e.g. ./tmp/recordings
    history_path: Optional[str] = Field(default=None, env="HISTORY_PATH") # e.g. ./tmp/agent_history


class DeepResearchToolSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_RESEARCH_TOOL_")

    max_parallel_browsers: int = Field(default=3, env="MAX_PARALLEL_BROWSERS")
    save_dir: Optional[str] = Field(default=None, env="SAVE_DIR") # Base dir, task_id will be appended. Optional now.


class PathSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_PATHS_")
    downloads: Optional[str] = Field(default=None, env="DOWNLOADS") # e.g. ./tmp/downloads


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_SERVER_")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    logging_level: str = Field(default="ERROR", env="LOGGING_LEVEL")
    anonymized_telemetry: bool = Field(default=True, env="ANONYMIZED_TELEMETRY")
    mcp_config: Optional[Dict[str, Any]] = Field(default=None, env="MCP_CONFIG") # For controller's MCP client


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_", extra='ignore') # Root prefix

    llm: LLMSettings = Field(default_factory=LLMSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    agent_tool: AgentToolSettings = Field(default_factory=AgentToolSettings)
    research_tool: DeepResearchToolSettings = Field(default_factory=DeepResearchToolSettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)

    @field_validator('server', 'llm', 'browser', 'agent_tool', 'research_tool', 'paths', mode='before')
    @classmethod
    def ensure_nested_defaults(cls, v: Any) -> Any:
        # This ensures that even if MCP_SERVER__LOG_FILE is set but MCP_SERVER is not,
        # the ServerSettings object is still created.
        # Pydantic-settings usually handles this, but being explicit can help.
        if v is None:
            return {}
        return v

    def get_api_key_for_provider(self, provider_name: Optional[str], is_planner: bool = False) -> Optional[str]:
        """Retrieves the API key for a given provider, checking generic, then specific."""
        llm_settings_to_use = self.llm
        provider_to_use = provider_name if provider_name else (self.llm.planner_provider if is_planner else self.llm.provider)

        if is_planner:
            if self.llm.planner_api_key:
                return self.llm.planner_api_key.get_secret_value()
            # Fallback to main LLM settings if planner-specific key is not set, but provider is
            if self.llm.planner_provider and not self.llm.planner_api_key:
                 llm_settings_to_use = self.llm # Check main llm settings for this provider
            # if no planner provider, it will use main llm provider and its key

        if not provider_to_use: # Should not happen if called correctly
            return None

        # Check generic API key first for the relevant LLM settings (main or planner if planner_api_key was set)
        if not is_planner and llm_settings_to_use.api_key: # only main LLM has generic api_key
             return llm_settings_to_use.api_key.get_secret_value()

        provider_specific_key_name = f"{provider_to_use.lower()}_api_key"
        if hasattr(llm_settings_to_use, provider_specific_key_name):
            key_val = getattr(llm_settings_to_use, provider_specific_key_name)
            if key_val and isinstance(key_val, SecretStr):
                return key_val.get_secret_value()
        return None

    def get_endpoint_for_provider(self, provider_name: Optional[str], is_planner: bool = False) -> Optional[str]:
        """Retrieves the endpoint for a given provider."""
        llm_settings_to_use = self.llm
        provider_to_use = provider_name if provider_name else (self.llm.planner_provider if is_planner else self.llm.provider)

        if is_planner:
            if self.llm.planner_base_url:
                return self.llm.planner_base_url
            if self.llm.planner_provider and not self.llm.planner_base_url:
                llm_settings_to_use = self.llm # Check main llm settings for this provider

        if not provider_to_use:
            return None

        if not is_planner and llm_settings_to_use.base_url: # only main LLM has generic base_url
            return llm_settings_to_use.base_url

        provider_specific_endpoint_name = f"{provider_to_use.lower()}_endpoint"
        if hasattr(llm_settings_to_use, provider_specific_endpoint_name):
            return getattr(llm_settings_to_use, provider_specific_endpoint_name)
        return None

    def get_llm_config(self, is_planner: bool = False) -> Dict[str, Any]:
        """Returns a dictionary of LLM settings suitable for llm_provider.get_llm_model."""
        provider = self.llm.planner_provider if is_planner and self.llm.planner_provider else self.llm.provider
        model_name = self.llm.planner_model_name if is_planner and self.llm.planner_model_name else self.llm.model_name
        temperature = self.llm.planner_temperature if is_planner and self.llm.planner_temperature is not None else self.llm.temperature

        api_key = self.get_api_key_for_provider(provider, is_planner=is_planner)
        base_url = self.get_endpoint_for_provider(provider, is_planner=is_planner)

        config = {
            "provider": provider,
            "model_name": model_name,
            "temperature": temperature,
            "api_key": api_key,
            "base_url": base_url,
            "use_vision": self.agent_tool.use_vision if not is_planner else False, # Planners typically don't need vision
            "tool_calling_method": self.agent_tool.tool_calling_method if not is_planner else "auto",
            "max_input_tokens": self.agent_tool.max_input_tokens if not is_planner else None,
        }

        if provider == "azure_openai":
            config["azure_openai_api_version"] = self.llm.azure_openai_api_version
        elif provider == "ollama":
            config["ollama_num_ctx"] = self.llm.ollama_num_ctx
            config["ollama_num_predict"] = self.llm.ollama_num_predict
        elif provider == "openrouter":
            config["provider"] = "openai"

        return config

# Global settings instance, to be imported by other modules
settings = AppSettings()

# Example usage (for testing this file directly):
if __name__ == "__main__":
    try:
        print("Loaded AppSettings:")
        print(settings.model_dump_json(indent=2))
        print(f"\nLLM API Key for main provider ({settings.llm.provider}): {settings.get_api_key_for_provider(settings.llm.provider)}")
        if settings.llm.planner_provider:
            print(f"LLM API Key for planner provider ({settings.llm.planner_provider}): {settings.get_api_key_for_provider(settings.llm.planner_provider, is_planner=True)}")

        print("\nMain LLM Config for get_llm_model:")
        print(settings.get_llm_config())
        if settings.llm.planner_provider:
            print("\nPlanner LLM Config for get_llm_model:")
            print(settings.get_llm_config(is_planner=True))
    except Exception as e:
        print(f"Error during settings load or test: {e}")
        import os
        print("MCP_RESEARCH_TOOL_SAVE_DIR:", os.getenv("MCP_RESEARCH_TOOL_SAVE_DIR"))
