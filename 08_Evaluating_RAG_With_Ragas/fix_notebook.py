import json

# Read the notebook
with open('Evaluating_RAG_with_Ragas_(2025)_AI_Makerspace.ipynb', 'r') as f:
    notebook = json.load(f)

# Find and fix the problematic line
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        for i, line in enumerate(cell['source']):
            if 'format|_messages' in line:
                # Replace the problematic line
                cell['source'][i] = line.replace('format|_messages', 'format_messages')
                print(f"Fixed line: {line.strip()}")

# Write the fixed notebook
with open('Evaluating_RAG_with_Ragas_(2025)_AI_Makerspace_fixed.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)

print("Notebook has been fixed and saved as 'Evaluating_RAG_with_Ragas_(2025)_AI_Makerspace_fixed.ipynb'") 