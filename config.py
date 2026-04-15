import yaml
from typing import Any
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class YamlSettingSource(PydanticBaseSettingsSource):
    def __init__(
        self, settings_cls: type[BaseSettings], yaml_file: str = "config.yaml"
    ):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file

    def get_field_value(self, field, field_name):
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        return self._read_yaml()

    def _read_yaml(self) -> dict[str, Any]:
        file_path = Path(__file__).parent / self.yaml_file
        if not file_path.exists():
            return {}

        with file_path.open("r", encoding="utf-8") as f:
            config_yaml = yaml.safe_load(f) or {}

        return config_yaml.get("app", {})


class KISSetting(BaseModel):
    base_url: str
    account_num: str
    account_code: str
    appkey: str
    appsecret: str


class AppSettings(BaseSettings):
    kis: KISSetting

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: BaseSettings,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlSettingSource(settings_cls),
            file_secret_settings,
        )


settings = AppSettings()
