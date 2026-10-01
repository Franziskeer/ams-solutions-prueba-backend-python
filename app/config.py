import os


class Settings:
    provider_base_url: str = os.getenv("PROVIDER_BASE_URL", "http://localhost:3001")
    provider_api_key: str = os.getenv("PROVIDER_API_KEY", "test-dev-2026")


settings = Settings()
