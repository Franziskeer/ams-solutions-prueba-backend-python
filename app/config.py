import os


class Settings:
    provider_base_url: str = os.getenv("PROVIDER_BASE_URL", "http://localhost:3001")
    provider_api_key: str = os.getenv("PROVIDER_API_KEY", "test-dev-2026")
    delivery_workers: int = int(os.getenv("DELIVERY_WORKERS", "10"))
    retry_attempts: int = int(os.getenv("RETRY_ATTEMPTS", "5"))
    retry_wait_initial: float = float(os.getenv("RETRY_WAIT_INITIAL", "0.5"))
    retry_wait_max: float = float(os.getenv("RETRY_WAIT_MAX", "10"))


settings = Settings()
