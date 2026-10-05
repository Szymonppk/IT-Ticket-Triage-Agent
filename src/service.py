import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAIChatCompletion,
    AzureChatPromptExecutionSettings,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory
from src.schemas import TicketTriageResult

load_dotenv()


class TicketTriageService:
    
    def __init__(self):
        self.kernel = Kernel()
        self._setup_chat_service()

    def _setup_chat_service(self):
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if azure_key and azure_key != "your_api_key":
            service = AzureChatCompletion(
                service_id="triage_chat",
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=azure_key,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            )
        elif openai_key and openai_key != "your_openai_api_key":
            service = OpenAIChatCompletion(
                service_id="triage_chat",
                ai_model_id=os.getenv("OPENAI_MODEL_ID"),
                api_key=openai_key,

            )
        else:
            raise ValueError("No valid API key found for Azure or OpenAI")

        self.kernel.add_service(service)

    async def analyze_ticket(self, user_ticket: str) -> TicketTriageResult:
        chat_service = self.kernel.get_service(service_id="triage_chat")

        system_prompt = (
            "You are expert IT support agent (L1/L2 Support).\n"
            "Your job is to analyze incoming tickets from employees\n"
            "You have to classify category, priority, provide summary and confidence score\n"
            "Answer directly with define response schema"
        )

        history = ChatHistory()
        history.add_system_message(system_prompt)
        history.add_user_message(f"Analyze the following IT ticket:\n{user_ticket}")

        if isinstance(chat_service, AzureChatCompletion):
            settings = AzureChatPromptExecutionSettings(
                temperature=0.1,
                response_format=TicketTriageResult,
            )
        else:
            settings = OpenAIChatPromptExecutionSettings(
                temperature=0.1,
                response_format=TicketTriageResult
            )

        response = await chat_service.get_chat_message_content(
            chat_history=history,
            settings=settings
        )
        print(f"Type: {type(response)}\n Response: {response}")
        raw_json_str = str(response)

        result_object = TicketTriageResult.model_validate_json(raw_json_str)

        print(f"Type result object: {type(result_object)}")
        return result_object

async def main():
    service = TicketTriageService()

    sample_ticket = (
        "I have problem with my computer\n"
        "I can't switch it on so i can't even start my work\n"
        "Problem started this morning after yesterday's update"
    )

    triage_result = await service.analyze_ticket(sample_ticket)

    print(triage_result.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())