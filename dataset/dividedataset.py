import json

def divide_json(input_file, output_prefix, num_files):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_records = len(data)
    records_per_file = total_records // num_files

    for i in range(num_files):
        start_index = i * records_per_file
        end_index = (i + 1) * records_per_file if i < num_files - 1 else total_records
        output_file = f"{output_prefix}_{i + 1}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data[start_index:end_index], f, ensure_ascii=False, indent=4)

# Use a função para dividir o arquivo JSON em 20 partes
divide_json("DREdataset_clean.json", "docs/DRE", 20)
