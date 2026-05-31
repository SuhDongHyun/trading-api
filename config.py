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
    """config.yaml의 app 섹션을 Pydantic Settings 입력으로 변환한다."""

    def __init__(
        self, settings_cls: type[BaseSettings], yaml_file: str = "config.yaml"
    ):
        """읽어올 YAML 파일 이름을 저장한다."""

        super().__init__(settings_cls)
        self.yaml_file = yaml_file

    def get_field_value(self, field, field_name):
        """개별 필드 조회를 사용하지 않음을 Pydantic에 알린다."""

        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        """Pydantic Settings가 사용할 YAML 설정 dict를 반환한다."""

        return self._read_yaml()

    def _read_yaml(self) -> dict[str, Any]:
        """config.yaml 파일에서 app 섹션만 읽어 반환한다."""

        file_path = Path(__file__).parent / self.yaml_file
        if not file_path.exists():
            return {}

        with file_path.open("r", encoding="utf-8") as f:
            config_yaml = yaml.safe_load(f) or {}

        return config_yaml.get("app", {})


class KISSetting(BaseModel):
    """한국투자증권 Open API 접속 정보 묶음."""

    base_url: str
    account_num: str
    account_code: str
    appkey: str
    appsecret: str


class FredSetting(BaseModel):
    """FRED API 접속 정보 묶음."""

    api_key: str


class AppSettings(BaseSettings):
    """환경변수, .env, config.yaml을 병합한 애플리케이션 설정."""

    kis: KISSetting
    fred: FredSetting

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
        """설정 우선순위에 config.yaml 소스를 추가한다."""

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlSettingSource(settings_cls),
            file_secret_settings,
        )


settings = AppSettings()
