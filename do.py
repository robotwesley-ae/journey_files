import os
import json
from openai import OpenAI
from openpyxl import Workbook

# Initialize the OpenAI client with your API key
client = OpenAI(api_key="your_api_key_here")

# Define the directory where your text files are stored
folder_path = 'processed_files'

# Define a default system message
default_system_message = "You are a text content analyzer. Your job is to call the analyze_text_content tool to analyze the text content provided by the user."

# Path to the enum file
enum_file_path = 'categories.txt'

# Read enum values from the file
with open(enum_file_path, 'r', encoding='utf-8') as file:
    enum_values = [line.strip() for line in file.readlines()]

# Placeholder for tools schema
tools = [
  {
    "type": "function",
    "function": {
      "name": "analyze_text_content",
      "description": "Analyze the text content based on various parameters",
      "parameters": {
        "type": "object",
        "properties": {
          "Topic": {
            "type": "string",
            "description": "A sentence expressing the main topic of the text"
          },
          "Subjects": {
            "type": "string",
            "description": "A sentence expressing the main subjects of the text"
          },
          "Content note": {
            "type": "array",
            "description": "One sentence note for each paragraph in the text. Each sentence prefixed by order number in parent text."
          },
          "Primary category": {
            "type": "string",
            "description": "The primary category of the text",
            "enum": enum_values
          },
          "Secondary category": {
            "type": "string",
            "description": "The secondary category of the text. This should be different than the primary category!",
            "enum": enum_values
          },
          "Tertiary category": {
            "type": "string",
            "description": "The tertiary category of the text. This should be different than the primary and secondary categories!",
            "enum": enum_values
          }
        },
        "required": ["Topic", "Subjects", "Content note", "Primary category", "Secondary category", "Tertiary category"]
      },
    }
  }
]

# Initialize a new Excel workbook and select the active worksheet
wb = Workbook()
ws = wb.active
ws.title = "API Responses"

# Define your headers based on the tool parameters you expect in every response
headers = ['Filename', 'Topic', 'Subjects', 'Content note', 'Primary category', 'Secondary category', 'Tertiary category']
ws.append(headers)

# Iterate over each file in the folder and process them
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        
        messages = [
            {"role": "system", "content": default_system_message},
            {"role": "user", "content": file_content}
        ]
        
        try:
            completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                # Assuming tools configuration is correctly defined above
                tools=tools,
                tool_choice="auto"
            )
            # Assuming the first 'tool_calls' response contains the arguments we need
            # Parsing the 'arguments' field from the first 'tool_calls' entry
            if completion['choices'] and completion['choices'][0]['message']['tool_calls']:
                arguments_str = completion['choices'][0]['message']['tool_calls'][0]['function']['arguments']
                arguments = json.loads(arguments_str.replace('\n', ''))  # Adjust parsing as necessary

                # Prepare row data
                row_data = [filename]
                for header in headers[1:]:  # Skip 'Filename' since it's already added
                    row_data.append(arguments.get(header, ''))
                
                # Append the row to the worksheet
                ws.append(row_data)
                
        except Exception as e:
            print(f"An error occurred with file {filename}: {e}")

# Define the path for the output Excel file
output_excel_path = 'api_responses.xlsx'

# Save the workbook
wb.save(filename=output_excel_path)

print(f"Responses have been written to {output_excel_path}.")