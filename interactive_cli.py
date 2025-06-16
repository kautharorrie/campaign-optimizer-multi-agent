from agents.interactive_session import InteractiveSession
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

def main():
    session = InteractiveSession()
    session_id = session.start_session()

    console.print(Panel.fit(
        "Interactive Campaign Analysis Session Started\n"
        "Type 'exit' to end the session\n"
        "Type 'history' to see conversation history"
    ))

    while True:
        try:
            user_input = console.input("\n[bold blue]You:[/] ")

            if user_input.lower() == 'exit':
                break

            if user_input.lower() == 'history':
                history = session.get_session_history(session_id)
                for msg in history:
                    color = {
                        'USER_INPUT': 'blue',
                        'SYSTEM_RESPONSE': 'green',
                        'USER_FEEDBACK': 'yellow',
                        'SYSTEM_REFINEMENT': 'cyan'
                    }.get(msg['type'], 'white')

                    console.print(f"\n[{color}]{msg['type']}:[/]")
                    console.print(Markdown(msg['content']))
                continue

            response = session.process_message(session_id, user_input)

            if response['type'] == 'refinement':
                console.print("\n[bold cyan]Refined Response:[/]")
            else:
                console.print("\n[bold green]Response:[/]")

            console.print(Markdown(response['content']))

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")

    console.print("\n[bold]Session ended[/]")

if __name__ == "__main__":
    main()
