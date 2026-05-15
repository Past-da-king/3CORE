import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set. "
            f"Refusing to start with insecure defaults."
        )
    return value


def _split_csv(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings(BaseSettings):
    # We store list-shaped settings as raw strings so pydantic-settings doesn't try
    # to JSON-parse plain comma-separated env values.
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    PROJECT_NAME: str = "3CORE Portal"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = _required("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'local_pm_tool.db'))}",
    )

    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")

    # Backblaze B2 (S3-compatible). All required for uploads.
    B2_ENDPOINT_URL: str = os.getenv("B2_ENDPOINT_URL", "https://s3.us-east-005.backblazeb2.com")
    B2_ACCESS_KEY_ID: str = os.getenv("B2_ACCESS_KEY_ID", "")
    B2_SECRET_ACCESS_KEY: str = os.getenv("B2_SECRET_ACCESS_KEY", "")
    B2_BUCKET_NAME: str = os.getenv("B2_BUCKET_NAME", "3core-storage")
    B2_REGION: str = os.getenv("B2_REGION", "us-east-005")

    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
    ALLOWED_UPLOAD_EXTENSIONS_RAW: str = os.getenv(
        "ALLOWED_UPLOAD_EXTENSIONS",
        # Broad set covering real construction / project-office uploads:
        # documents, spreadsheets, presentations, images (incl. phone HEIC),
        # CAD drawings, archives, and email exports. Executables/scripts
        # remain blocked by omission.
        "pdf,doc,docx,xls,xlsx,xlsm,ppt,pptx,txt,csv,rtf,odt,ods,odp,"
        "png,jpg,jpeg,gif,bmp,tif,tiff,webp,heic,heif,svg,"
        "dwg,dxf,dwf,"
        "zip,rar,7z,tar,gz,"
        "msg,eml",
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return _split_csv(self.CORS_ORIGINS_RAW)

    @property
    def ALLOWED_UPLOAD_EXTENSIONS(self) -> List[str]:
        return _split_csv(self.ALLOWED_UPLOAD_EXTENSIONS_RAW)


settings = Settings()
