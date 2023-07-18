import json
import csv
import os

def main(directory, timestamp, output_file):
    jsonFiles = []
    for filename in os.listdir(directory):
        if filename.endswith('json'):
            jsonFiles.append(filename)
    jsonFiles.sort(key=str.lower)
    print(jsonFiles)
    rows = []
    for file in range(len(jsonFiles)):
        # Load JSON data from file
        print(f"Work with file... {directory}{jsonFiles[file]}")
        with open(directory + jsonFiles[file]) as json_file:
            data = json.load(json_file)

        # Extract relevant fields from JSON data

        for message in data['messages']:
            row = [
                message['id'],
                message['date'],
                message['date_unixtime'],
                message.get('edited', None),
                message.get('edited_unixtime', None),
                message.get('from', None),
                message.get('from_id', None),
                message['text'],
                # ''.join([text['text'] for text in message['text'] if 'text' in text]),
                message.get('photo', None)  # Use get() method with a default value
            ]
            rows.append(row)

        # Write the extracted data to a CSV file
    print(f"Saving data of file")
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['ID', 'Date', 'Date_Unix', 'Edited', 'Edited_Unix', 'From', 'From_id', 'Text', 'Photo'])
        writer.writerows(rows)

