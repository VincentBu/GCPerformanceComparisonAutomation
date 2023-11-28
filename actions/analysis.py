import os
import json
import pandas as pd
import markdown
from io import StringIO
from markdown.extensions.tables import TableExtension


def extract_tables_and_tiltes_from_markdown(markdown_file_path: os.PathLike):
    # Read the markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    # Convert markdown to HTML
    tables_html = markdown.markdown(markdown_text, extensions=[TableExtension()])

    # Extract tables using Pandas
    valid_title_list = [
        'Large Regressions', 'Large Improvements', 
        'Regressions', 'Improvements', 
        'Stale Regressions', 'Stale Improvements'
    ]
    tables = dict()
    for title, table in zip(valid_title_list, pd.read_html(StringIO(tables_html))[-len(valid_title_list):]):
        tables[title] = json.loads(table.to_json(orient='records'))

    return tables
