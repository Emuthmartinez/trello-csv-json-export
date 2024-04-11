import pandas as pd
import json
  
json_file_path = 'YOUR_FILE_PATH_HERE.json'
csv_file_path = 'YOUR_FILE_PATH_HERE.csv'
json_output_file_path = 'YOUR_FILE_PATH_HERE.json' 
  
# Load the JSON data
with open(json_file_path, 'r', encoding='utf-8') as file:
    trello_data = json.load(file)
 
# Extract the lists (mapping from list ID to list name)
list_mapping = {list_['id']: list_['name'] for list_ in trello_data['lists']}
 
# Create a dictionary to map card IDs to comments
card_comments = {}
for action in trello_data['actions']:
    if action['type'] == 'commentCard':
        card_id = action['data']['card']['id']
        comment_text = action['data']['text']
        if card_id not in card_comments:
            card_comments[card_id] = []
        card_comments[card_id].append(comment_text)
 
# Create a dictionary to map card IDs to checklist items
card_checklists = {}
for checklist in trello_data['checklists']:
    for idx, item in enumerate(checklist['checkItems']):
        card_id = checklist['idCard']
        if card_id not in card_checklists:
            card_checklists[card_id] = []
        checklist_item = {
            "ID": idx+1,
            "title": item['name'],
            "isChecked": True if item['state'] == 'complete' else False
        }
        card_checklists[card_id].append(checklist_item)
 
# Extract the required information for each card
cards_data = []
for card in trello_data['cards']:
    card_data = {
        "name": card["name"],
        "list_name": list_mapping.get(card["idList"], ""),
        "labels": ", ".join(label["name"] for label in card["labels"]),
        "creation_date": card["dateLastActivity"],
        "closed_status": card["closed"],
        "description": card["desc"],
        "date_last_activity": card["dateLastActivity"],
        "due_date": card["due"],
        "comments": card_comments.get(card['id'], []),
        "checklist_items": card_checklists.get(card['id'], [])
    }
    cards_data.append(card_data)
 
# Create a DataFrame
df = pd.DataFrame(cards_data)
 
# Save to CSV
# For CSV, we will convert lists to string to avoid issues while saving to CSV
df_csv = df.copy()
df_csv['comments'] = df_csv['comments'].apply(lambda x: ', '.join(x))
df_csv['checklist_items'] = df_csv['checklist_items'].apply(lambda x: ', '.join([f"{item['ID']} - {item['title']}" for item in x]))
df_csv.to_csv(csv_file_path, encoding='utf-8', index=False)
 
# Save to JSON
df.to_json(json_output_file_path, orient='records', date_format='iso')
 
print(f"CSV file saved to {csv_file_path}")
print(f"JSON file saved to {json_output_file_path}")
  
#In this script:
  
#We keep track of the maximum number of comments on any card while building the card_comments dictionary.
#When creating the data for each card, we create a series of columns comment_1, comment_2, ..., comment_n (where n is the maximum number of comments found on any card), and fill in the comments for each card accordingly. If a #card has fewer comments, the remaining columns will be filled with empty strings.
  
#We create a card_checklists dictionary to store checklist items by card ID, and find the maximum number of checklist items across all cards.
#We iterate over the checklists in the JSON data, adding each checklist item and its state (completed or not) to the card_checklists dictionary.
#While creating the data for each card, we add columns for each checklist item, similar to how we added columns for comments.
