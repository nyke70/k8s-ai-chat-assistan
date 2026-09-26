#"""Everything this app reads from the environment, in one place."""

import os

from dotenv import load_dotenv

# Copies the .env next to this file into the process environment.
# os.getenv below reads our settings back out of it, and the Anthropic
# library finds ANTHROPIC_API_KEY there on its own: we never pass it.
load_dotenv()

# --- model ---
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
STEP_LIMIT = 10         # how many times the agent may loop before giving up

# --- cluster ---
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8080/mcp")
NAMESPACE = os.getenv("NAMESPACE", "default")

SYSTEM_PROMPT = f"""
You are a read-only Kubernetes assistant. The default namespace is {NAMESPACE}.

Gather evidence before you conclude. Look at pods, then events, then logs.
A pod can report phase Running while its container sits in CrashLoopBackOff,
so read the waiting reason and the restart count, not the phase alone.

Report only what a tool returned. If a tool returns nothing, say so.
If a fix needs a write, describe the command and do not run it.
"""