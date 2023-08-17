def read_text_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    data = data.replace("'", "\"")
    print(data)
    json_data = f"[{data}]"
    return json_data
