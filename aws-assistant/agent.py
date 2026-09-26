from datetime import datetime, timezone

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

from config import MODEL, STEP_LIMIT, SYSTEM_PROMPT
from tools import load_tools


async def ask(question, history=()):
    model = ChatAnthropic(
        model=MODEL,
        temperature=0,
    )

    today = datetime.now(timezone.utc).date().isoformat()

    prompt = (
        SYSTEM_PROMPT
        + f"\nCurrent UTC date supplied by the application: {today}.\n"
    )

    messages = list(history) + [
        {"role": "user", "content": question}
    ]

    async with load_tools() as available_tools:
        assistant = create_agent(
            model=model,
            tools=available_tools,
            system_prompt=prompt,
        )

        result = await assistant.ainvoke(
            {"messages": messages},
            config={"recursion_limit": STEP_LIMIT},
        )

    answer = result["messages"][-1].text

    called = list(
        dict.fromkeys(
            message.name
            for message in result["messages"]
            if message.type == "tool" and message.name
        )
    )

    return answer, called


async def tool_names():
    async with load_tools() as available_tools:
        return sorted(tool.name for tool in available_tools)