# create_env.py
import os

env_variables = [
    "BISKIT_USER",
    "BISKIT_USER_PW",
    "POSTGRES_DB",
    "TEST_DB",
    "DB_ROOT_PASSWORD",
    "CORS_ORIGINS",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "PROJECT_NAME",
    "NICKNAME_API",
    "REFRESH_SECRET_KEY",
    "REFRESH_TOKEN_EXPIRE_MINUTES",
    "SMTP_SERVER",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "DOCS_USER",
    "DOCS_PW",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "BUCKET_NAME",
    "LOGO_URL",
    "FIRESTORE_URL",
    "S3_URL",
    "REDIS_HOST",
]

with open(".env", "w") as f:
    for var in env_variables:
        value = os.environ.get(f"{var}")
        f.write(f"{var}={value}\n")
