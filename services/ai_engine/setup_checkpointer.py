from dotenv import load_dotenv
import os

from langgraph.checkpoint.postgres import PostgresSaver


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL loaded:", bool(DATABASE_URL))

with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    checkpointer.setup()

print("Checkpoint tables created successfully")