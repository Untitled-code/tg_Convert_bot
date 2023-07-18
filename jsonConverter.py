import json
import csv
import logging


def main(filename, directory, timestamp, outputFile):
    # Load JSON data from file
    with open(filename) as json_file:
        data = json.load(json_file)

    print(f'Output file is made: {outputFile}')
    logging.debug(f'Output file is made: {outputFile}')
    # Extract relevant fields from JSON data
    rows = []
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
    with open(outputFile, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['ID', 'Date', 'Date_Unix', 'Edited', 'Edited_Unix', 'From', 'From_id', 'Text', 'Photo'])
        writer.writerows(rows)
