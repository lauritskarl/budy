from pathlib import Path
from typing import Annotated, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from sqlmodel import Session
from typer import Exit, Option, get_app_dir

from budy.config import APP_NAME, BankConfig, Settings, settings
from budy.database import engine
from budy.services.transaction import import_transactions
from budy.views.messages import render_error
from budy.views.transaction import render_import_summary

console = Console()


def print_next_steps(
    header: str = "\n[bold]Explore your data with these commands:[/]",
) -> None:
    """Prints a list of suggested commands for the user to try."""
    console.print(header)
    console.print("• View monthly overview:   [green]budy reports month[/]")
    console.print("• See top payees:          [green]budy reports payees[/]")
    console.print("• Analyze spending habits: [green]budy reports weekday[/]")
    console.print("• Check for outliers:      [green]budy reports volatility[/]")


def run_setup(
    first_name: Annotated[Optional[str], Option(help="Your first name.")] = None,
    last_name: Annotated[Optional[str], Option(help="Your last name.")] = None,
) -> None:
    """Initialize the configuration file with your details."""
    app_dir = Path(get_app_dir(APP_NAME))
    app_dir.mkdir(parents=True, exist_ok=True)
    config_path = app_dir / "config.toml"

    imported_banks = None

    # 1. Overwrite Check (First Step)
    if config_path.exists():
        console.print(f"[yellow]Config file found at {config_path}[/]")

        if not Confirm.ask("Do you want to overwrite it?"):
            console.print("[yellow]Operation cancelled.[/]")
            raise Exit()

        if Confirm.ask("Import bank configurations from this existing file?"):
            try:
                # Load settings from the current file on disk
                current_settings = Settings.load()
                imported_banks = current_settings.banks
                console.print(
                    f"[green]✓ Successfully loaded {len(imported_banks)} banks.[/]"
                )
            except Exception as e:
                console.print(f"[red]Failed to import banks: {e}[/]")
                if not Confirm.ask("Continue with default banks?"):
                    raise Exit()

    # 2. Gather User Info
    if not first_name:
        first_name = Prompt.ask("Your first name")
    if not last_name:
        last_name = Prompt.ask("Your last name")

    # 3. Interactive Currency Selection
    console.print("\n[bold]Select your currency:[/]")
    console.print("1. [green]EUR[/] (€)")
    console.print("2. [green]USD[/] ($)")
    console.print("3. [green]GBP[/] (£)")
    console.print("4. Other (type custom symbol)")

    choice = Prompt.ask(
        "Choose a number", choices=["1", "2", "3", "4"], default="1", show_choices=False
    )

    if choice == "1":
        currency = "€"
    elif choice == "2":
        currency = "$"
    elif choice == "3":
        currency = "£"
    else:
        currency = Prompt.ask("Enter currency symbol")

    # 4. Prepare Settings
    defaults = Settings(
        first_name=first_name,
        last_name=last_name,
        currency_symbol=currency,
    )

    if imported_banks:
        defaults.banks = imported_banks

    # 5. Save Configuration
    save_config(config_path, defaults)

    # Update global settings in memory so imports work immediately without reload
    settings.first_name = defaults.first_name
    settings.last_name = defaults.last_name
    settings.currency_symbol = defaults.currency_symbol
    settings.banks = defaults.banks

    console.print(f"\n[green]✓ Configuration saved to {config_path}[/]")
    console.print(
        f"\nWelcome, [bold cyan]{first_name} {last_name}[/]! You are all set."
    )

    # 6. Import Transactions Workflow
    if Confirm.ask("\nWould you like to import transactions from a bank CSV now?"):
        handle_import_workflow(config_path, defaults)
    else:
        console.print("\n[yellow]You can import transactions later using:[/]")
        console.print(
            "[green]budy transactions import --bank <bank_name> --file <path_to_csv>[/]"
        )
        print_next_steps(header="\n[bold]After importing, explore your data with:[/]")


def save_config(path: Path, settings_obj: Settings):
    """Writes the settings object to a TOML file."""
    toml_content = f"""# Budy Configuration
currency_symbol = "{settings_obj.currency_symbol}"
first_name = "{settings_obj.first_name}"
last_name = "{settings_obj.last_name}"

# Bank Configurations
"""
    for bank_key, bank_config in settings_obj.banks.items():
        toml_content += f"\n[banks.{bank_key}]\n"
        toml_content += f'delimiter = "{bank_config.delimiter}"\n'
        toml_content += f'decimal = "{bank_config.decimal}"\n'
        toml_content += f'encoding = "{bank_config.encoding}"\n'
        toml_content += f'date_col = "{bank_config.date_col}"\n'
        toml_content += f'amount_col = "{bank_config.amount_col}"\n'
        toml_content += f'debit_credit_col = "{bank_config.debit_credit_col}"\n'
        toml_content += f'debit_value = "{bank_config.debit_value}"\n'

        if bank_config.receiver_col:
            toml_content += f'receiver_col = "{bank_config.receiver_col}"\n'
        if bank_config.description_col:
            toml_content += f'description_col = "{bank_config.description_col}"\n'

    with open(path, "w", encoding="utf-8") as f:
        f.write(toml_content)


def handle_import_workflow(config_path: Path, current_settings: Settings):
    """Handles the interactive import process."""
    console.print("\n[bold]Select a bank:[/]")
    bank_names = list(current_settings.banks.keys())

    for i, name in enumerate(bank_names, 1):
        console.print(f"{i}. {name}")
    console.print(f"{len(bank_names) + 1}. Other / Configure new bank")

    choices = [str(i) for i in range(1, len(bank_names) + 2)]
    choice = Prompt.ask(
        "Choose a number", choices=choices, default="1", show_choices=False
    )

    selected_bank_name = None

    # Handle "Other"
    if choice == str(len(bank_names) + 1):
        if Confirm.ask("Define new bank parameters now?"):
            # Define new bank
            new_bank_name = Prompt.ask(
                "Enter unique bank identifier (e.g., 'my_bank')"
            ).lower()
            if new_bank_name in current_settings.banks:
                console.print(f"[red]Bank '{new_bank_name}' already exists.[/]")
                return

            console.print("[dim]Enter CSV format details:[/dim]")
            new_bank = BankConfig(
                delimiter=Prompt.ask("Delimiter", default=","),
                decimal=Prompt.ask("Decimal separator", default="."),
                date_col=Prompt.ask("Date column header"),
                amount_col=Prompt.ask("Amount column header"),
                debit_credit_col=Prompt.ask("Debit/Credit column header"),
                debit_value=Prompt.ask(
                    "Value indicating debit (e.g. 'D')", default="D"
                ),
                receiver_col=Prompt.ask(
                    "Receiver column header (optional)", default=None
                ),
                description_col=Prompt.ask(
                    "Description column header (optional)", default=None
                ),
                encoding="utf-8",  # Defaulting for simplicity
            )

            # Update settings and save immediately
            current_settings.banks[new_bank_name] = new_bank
            settings.banks[new_bank_name] = new_bank  # Update global memory
            save_config(config_path, current_settings)

            selected_bank_name = new_bank_name
            console.print(f"[green]✓ Bank '{new_bank_name}' saved to config.[/]")
        else:
            # Define Later - Show suggestion
            console.print(
                "\n[yellow]To configure later, add this to your config.toml:[/]"
            )
            console.print("""
[banks.custom_bank]
delimiter = ","
decimal = "."
date_col = "Date"
amount_col = "Amount"
debit_credit_col = "Type"
debit_value = "D"
            """)
            console.print("\nThen run:")
            console.print(
                "[green]budy transactions import --bank custom_bank --file <path>[/]"
            )
            print_next_steps(
                header="\n[bold]After importing, explore your data with:[/]"
            )
            return
    else:
        selected_bank_name = bank_names[int(choice) - 1]

    # Perform Import
    if selected_bank_name:
        file_path_str = Prompt.ask("Enter the path to your CSV file")
        file_path = Path(file_path_str)

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/]")
            return

        console.print(f"\nImporting from [cyan]{selected_bank_name}[/]...")
        try:
            with Session(engine) as session:
                transactions = import_transactions(
                    session=session,
                    bank_name=selected_bank_name,
                    file_path=file_path,
                    dry_run=False,
                )
                console.print(
                    render_import_summary(
                        transactions=transactions,
                        filename=file_path.name,
                        dry_run=False,
                    )
                )
                print_next_steps()
        except Exception as e:
            console.print(render_error(message=f"Import failed: {e}"))
