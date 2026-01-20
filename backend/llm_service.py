import sys
import os
import json
import re
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.main import (
    hotel_tools,
    hotel_system_prompt,
    available_functions,
    init_db,
)

try:
    from groq import Groq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None


def clean_response_text(text: str) -> str:
    """Remove hallucinated function calls from response text."""
    text = re.sub(r"<function=\w+>.*?</function>", "", text, flags=re.DOTALL)
    text = re.sub(
        r'\{["\']?function["\']?\s*:\s*["\']?\w+["\']?.*?\}', "", text, flags=re.DOTALL
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text


class LLMService:
    def __init__(self):
        if not GROQ_AVAILABLE:
            raise ImportError("groq package not installed. Run: uv pip install groq")
        self.client = Groq()
        self.model = "llama-3.3-70b-versatile"
        init_db()

    async def process_message(
        self,
        user_message: str,
        messages: list[dict[str, Any]],
        sentiment: str | None = None,
        score: float = 0.0,
    ) -> tuple[str, list[dict[str, Any]]]:
        content = user_message
        if sentiment:
            content += f" [Detected Sentiment: {sentiment} ({score:.2f})]"
        messages.append({"role": "user", "content": content})

        max_iterations = 5
        iteration = 0
        final_response = ""

        while iteration < max_iterations:
            iteration += 1

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=hotel_tools,
                tool_choice="auto",
                temperature=0.1,
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                final_response = response_message.content or ""
                messages.append({"role": "assistant", "content": final_response})
                break

            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            }
            messages.append(assistant_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                function_to_call = available_functions.get(function_name)
                if function_to_call:
                    function_response = function_to_call(**function_args)
                else:
                    function_response = json.dumps(
                        {"error": f"Unknown tool: {function_name}"}
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response,
                    }
                )

        return clean_response_text(final_response), messages

    def create_initial_messages(self) -> list[dict[str, Any]]:
        return [{"role": "system", "content": hotel_system_prompt}]
