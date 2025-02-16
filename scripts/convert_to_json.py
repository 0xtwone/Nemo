import json


def main():
    # Define the path to the target file
    file_path = 'scripts/binance_eth_trend.py'
    try:
        # Open and read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        
        # Create a dictionary with the file name and its content
        result = {
            'filename': file_path,
            'content': file_content
        }
        
        # Convert the dictionary into a JSON formatted string
        json_output = json.dumps(result, indent=4, ensure_ascii=False)
        
        # Output the JSON string
        print(json_output)
    except Exception as e:
        print(f'Error reading file: {e}')


if __name__ == '__main__':
    main() 