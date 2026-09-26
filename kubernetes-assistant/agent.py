"""The agent: a model, some tools, a loop. The same three pieces as Day 1."""

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

from config import MODEL, STEP_LIMIT, SYSTEM_PROMPT
from tools import load_tools

model = ChatAnthropic(model=MODEL)


async def ask(question, history=()):
    """Ask one question. Returns the answer and the tools the model called."""
    agent = create_agent(model, await load_tools(), system_prompt=SYSTEM_PROMPT)

    messages = list(history) + [{"role": "user", "content": question}]
    result = await agent.ainvoke({"messages": messages}, config={"recursion_limit": STEP_LIMIT})

    called = [m.name for m in result["messages"] if m.type == "tool"]
    return result["messages"][-1].text, called


async def tool_names():
    """The tool names the server offers. Change read_only in mcp-config.toml to compare."""
    return sorted(t.name for t in await load_tools())