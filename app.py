import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from rich.console import Console
from rich.table import Table

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

api_key = 'AIzaSyDq-7YfKkDvkyGLce7CRvwrDbVqQwyseHc'
search_engine = '54eb44f83140643c3'
console = Console()  # Create a Console instance for rich output

def perform_search(query, site=None, start=1):
    console.print(f"[bold blue]Performing search for '{query}' on site '{site}' (start={start})...[/bold blue]")
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': query,
        'key': api_key,
        'cx': search_engine,
        'start': start
    }
    
    if site:
        # Automatically prepend 'https://www.' if it doesn't already start with 'http://' or 'https://'
        if not site.startswith(('http://', 'https://')):
            site = f"https://www.{site}"
        params['q'] += f" site:{site}"


    console.print(f"[green]Sending request to API with params:[/green]")
    console.print(params)
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        console.print(f"[red]Error: Received status code {response.status_code}[/red]")
        return []

    results = response.json()
    new_links = []

    if 'items' in results:
        console.print(f"[bold green]Found {len(results['items'])} results.[/bold green]")
        for item in results['items']:
            new_links.append(item['link'])

        # Limit to the most recent 20 links
        new_links = new_links[:20]
    else:
        console.print("[yellow]No items in the response.[/yellow]")

    return new_links  # Return new links found

@app.route('/search', methods=['POST'])
def search_api():
    console.print("[bold yellow]Received search request...[/bold yellow]")
    data = request.json
    search_query = data.get('query')
    site = data.get('site', None)
    page = data.get('page', 1)  # Get page number from request
    start_index = (page - 1) * 10 + 1  # Calculate start index for results

    # Perform the search
    new_links = perform_search(search_query, site, start=start_index)

    if new_links:
        console.print("[bold green]Returning new links found.[/bold green]")
        
        # Create a table to display the results
        table = Table(title="Search Results")
        table.add_column("Link", style="cyan", no_wrap=True)

        for link in new_links:
            table.add_row(link)

        console.print(table)

        return jsonify({"new_links": new_links}), 200
    else:
        console.print("[red]No new links found to return.[/red]")
        return jsonify({"message": "No new links found."}), 404

if __name__ == "__main__":
    console.print("[bold blue]Starting the search API...[/bold blue]")
    app.run(debug=True)
