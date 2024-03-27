# -*- coding: utf-8 -*-
import os
import re
import shutil
from docx import Document

def load_key_strings(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return [line.strip().lower() for line in file]

def normalize_text(text):
    """
    Convert text to lowercase and replace typographic apostrophes with ASCII apostrophes.
    """
    return text.lower().replace("\u2019", "'")

def file_contains_key_strings(filename, key_strings):
    content = normalize_text(read_file_content(filename))
    return any(normalize_text(key_string) in content for key_string in key_strings)

def move_file_to_review_folder(source_path, review_directory):
    ensure_directory_exists(review_directory)
    base_name = os.path.basename(source_path)
    # Change .docx to .txt in filename if necessary
    base_name = change_extension_to_txt(base_name)
    target_path = os.path.join(review_directory, base_name)
    if source_path.endswith('.docx'):
        # Convert .docx content to .txt and move
        content = read_file_content(source_path)
        with open(target_path, 'w', encoding='utf-8') as file:
            file.write(content)
        os.remove(source_path)  # Remove original .docx file
    else:
        shutil.move(source_path, target_path)

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def change_extension_to_txt(filename):
    return re.sub(r'\.docx$', '.txt', filename, flags=re.IGNORECASE)

def read_file_content(filename):
    if filename.endswith('.docx'):
        doc = Document(filename)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()

def clean_filename(filename):
    # Change .docx to .txt in filename
    filename = change_extension_to_txt(filename)
    name, ext = os.path.splitext(filename)
    clean_name = re.sub(r'\s+', '_', name)  # Replace spaces with underscores
    clean_name = re.sub(r'[^\w\-_\.]', '', clean_name)  # Remove special characters
    return f"{clean_name}{ext}"

def find_split_index(text, start_index, end_index):
  newline_index = text.rfind('\n', start_index, end_index)
  if newline_index != -1:
      return newline_index + 1  # Include the newline character
  else:
      word_boundary_index = text.rfind(' ', start_index, end_index)
      return word_boundary_index if word_boundary_index != -1 else end_index

def chunk_text(text, ideal_size=4000, tolerance=200):
  chunks = []
  start_index = 0
  while start_index < len(text):
      if len(text) - start_index <= ideal_size:
          chunks.append(text[start_index:])
          break
      end_index = start_index + ideal_size
      if len(text) > end_index and text[end_index] not in [' ', '\n']:
          end_index = find_split_index(text, start_index, min(len(text), end_index + tolerance))
      chunks.append(text[start_index:end_index])
      start_index = end_index
  return chunks

def process_files(directory):
  files = [f for f in os.listdir(directory) if f.endswith('.docx') or f.endswith('.txt')]
  counter = 1
  for filename in files:
      content = read_file_content(os.path.join(directory, filename))
      chunks = chunk_text(content)
      if 4000 < len(content) < 6000 and len(chunks) > 1:
          # Attempt to split in half, considering the nearest newline or word boundary
          half_index = find_split_index(content, len(content) // 2 - 200, len(content) // 2 + 200)
          chunks = [content[:half_index], content[half_index:]]
      for i, chunk in enumerate(chunks, 1):
          new_filename = f"{str(counter).zfill(3)}{'.' + str(i) if len(chunks) > 1 else ''}-{clean_filename(filename)}"
          with open(new_filename, 'w', encoding='utf-8') as file:
              file.write(chunk)
      counter += 1

def process_files_with_filter(directory, output_directory, key_strings_file, review_directory):
  ensure_directory_exists(output_directory)
  key_strings = load_key_strings(key_strings_file)
  files = [f for f in os.listdir(directory) if f.endswith('.docx') or f.endswith('.txt')]
  counter = 1
  for filename in files:
      filepath = os.path.join(directory, filename)
      if not file_contains_key_strings(filepath, key_strings):
          move_file_to_review_folder(filepath, review_directory)
          continue
      content = read_file_content(filepath)
      chunks = chunk_text(content)
      if 4000 < len(content) < 6000 and len(chunks) > 1:
          half_index = find_split_index(content, len(content) // 2 - 200, len(content) // 2 + 200)
          chunks = [content[:half_index], content[half_index:]]
      for i, chunk in enumerate(chunks, 1):
          new_filename = f"{str(counter).zfill(3)}{'.' + str(i) if len(chunks) > 1 else ''}-{clean_filename(filename)}"
          target_path = os.path.join(output_directory, new_filename)
          with open(target_path, 'w', encoding='utf-8') as file:
              file.write(chunk)
      counter += 1

# Example usage
directory = "files"  # Update this to your directory
output_directory = "processed_files"  # Update this for processed files
key_strings_file = "key_strings.txt"  # Update this to your key strings file
review_directory = "review"  # Update this to your review directory
process_files_with_filter(directory, output_directory, key_strings_file, review_directory)




