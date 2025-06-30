from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import (
    get_weather, search_web, send_email, capture_screen, get_screen_info,
    find_on_screen, click_on_screen, type_text, press_key_combination,
    open_application, close_application, get_running_processes, create_file,
    read_file_content, delete_file, list_directory, get_system_info,
    control_volume, window_management, scroll_page, run_command,
    remember_information, recall_information, add_task_to_memory,
    advanced_window_control, mouse_automation, keyboard_automation,
    manage_startup_programs, network_control, power_management
)

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
            # voice="Charon"
            voice="Aoede",
            temperature=0.9,
        ),
            tools=[
                get_weather,
                search_web,
                send_email,
                capture_screen,
                get_screen_info,
                find_on_screen,
                click_on_screen,
                type_text,
                press_key_combination,
                open_application,
                close_application,
                get_running_processes,
                create_file,
                read_file_content,
                delete_file,
                list_directory,
                get_system_info,
                control_volume,
                window_management,
                scroll_page,
                run_command,
                remember_information,
                recall_information,
                add_task_to_memory,
                advanced_window_control,
                mouse_automation,
                keyboard_automation,
                manage_startup_programs,
                network_control,
                power_management
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(

    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True,
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
