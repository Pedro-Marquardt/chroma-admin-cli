import typer
import json
import questionary
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from chromadb import HttpClient
from chromadb.config import Settings

app = typer.Typer(help="CLI for ChromaDB administration and exploration")
console = Console()
CONFIG_FILE = Path.home() / ".chroma_cli.json"

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def get_client(tenant="default_tenant", database="default_database"):
    cfg = load_config()
    if not cfg:
        console.print("[red]CLI not configured. Run 'chroma-cli config' first.[/red]")
        raise typer.Exit(1)

    host = cfg.get("host")
    port = int(cfg.get("port", 8000)) 
    user = cfg.get("user")
    password = cfg.get("password")

    settings = None
    if user and password:
        settings = Settings(
            chroma_client_auth_provider="chromadb.auth.basic_authn.BasicAuthClientProvider",
            chroma_client_auth_credentials=f"{user}:{password}",
        )

    return HttpClient(
        host=host,
        port=port,          
        tenant=tenant,
        database=database,
        settings=settings,  
    )

@app.command()
def config(
    host: str = typer.Option(..., prompt="ChromaDB Host URL"),
    user: str = typer.Option(default=None, prompt="ChromaDB Username (optional)", show_default=False),
    password: str = typer.Option(default=None, prompt="ChromaDB Password (optional)", hide_input=True, show_default=False),
    port: int = typer.Option(default=8000, prompt="ChromaDB HTTP Port (Default: 8000)", show_default=True),
):
    """Configures the base connection to ChromaDB."""
    config_data = {"host": host}
    if user:
        config_data["user"] = user
    if password:
        config_data["password"] = password
    if port:
        config_data["port"] = int(port)    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f)
    console.print("[green]Configuration saved to ~/.chroma_cli.json[/green]")

@app.command()
def explore(
    tenant: str = typer.Option("default_tenant", help="Tenant ID"),
    database: str = typer.Option("default_database", help="Database Name")
):
    """Opens an interactive menu to navigate collections and chunks."""
    client = get_client(tenant, database)

    # 1. Fetch Collections
    try:
        raw_collections = client.list_collections()
    except Exception as e:
        console.print(f"[red]Error listing collections: {e}[/red]")
        raise typer.Exit(1)
        
    if not raw_collections:
        console.print("[yellow]No collections found.[/yellow]")
        return

    collection_names = [getattr(c, 'name', str(c)) for c in raw_collections]

    # --- OUTER LOOP: COLLECTION NAVIGATION ---
    while True:
        console.clear()
        
        # Adding an exit option at the top of the list
        choices_collections = ["⬅️  Exit"] + collection_names
        
        chosen_collection = questionary.select(
            "Select a collection to explore:",
            choices=choices_collections
        ).ask()

        # Break the loop if the user selects Exit or presses Ctrl+C
        if not chosen_collection or chosen_collection == "⬅️  Exit":
            console.print("[green]Exiting exploration mode. Goodbye![/green]")
            break

        # 2. Load collection data
        try:
            collection = client.get_collection(name=chosen_collection)
            with console.status(f"Loading chunks from {chosen_collection}..."):
                data = collection.get(include=["documents", "metadatas", "embeddings"])
        except Exception as e:
            console.print(f"[red]Error loading collection data: {e}[/red]")
            console.input("\n[bold]Press [Enter] to try again...[/bold]")
            continue

        ids = data.get("ids", [])
        if not ids:
            console.print(f"[yellow]The collection {chosen_collection} is empty.[/yellow]")
            console.input("\n[bold]Press [Enter] to go back...[/bold]")
            continue

        # --- INNER LOOP: CHUNK NAVIGATION ---
        while True:
            console.clear()
            
            # Adding a back option at the top of the chunk list
            choices_chunks = ["⬅️  Back to Collections"] + ids
            
            chosen_chunk = questionary.select(
                f"[{chosen_collection}] Found {len(ids)} chunks. Choose one to inspect:",
                choices=choices_chunks
            ).ask()

            # Break inner loop to go back to collections if selected or Ctrl+C
            if not chosen_chunk or chosen_chunk == "⬅️  Back to Collections":
                break

            # 3. Display the data of the chosen chunk safely
            index = ids.index(chosen_chunk)
            
            text = data["documents"][index] if data.get("documents") is not None else "N/A"
            metadata = data["metadatas"][index] if data.get("metadatas") is not None else "N/A"
            
            # Handle the embedding array safely
            if data.get("embeddings") is not None:
                raw_embedding = data["embeddings"][index]
                embedding = raw_embedding.tolist() if hasattr(raw_embedding, "tolist") else raw_embedding
            else:
                embedding = []

            # Limiting the embedding display so it doesn't flood the terminal screen
            emb_preview = f"{embedding[:5]} ... ({len(embedding)} dimensions total)" if embedding else "No embedding found"

            # Beautiful print using Rich
            panel_content = f"""
[bold cyan]ID:[/bold cyan] {chosen_chunk}
[bold cyan]Metadata:[/bold cyan] {metadata}
[bold cyan]Embedding Preview:[/bold cyan] {emb_preview}
---
[bold green]Text:[/bold green]
{text}
            """
            console.clear()
            console.print(Panel(panel_content, title="Chunk Details", expand=False))
            
            # Pause to read the chunk before returning to the list
            console.input("\n[bold]Press [Enter] to return to the chunk list...[/bold]")

if __name__ == "__main__":
    app()