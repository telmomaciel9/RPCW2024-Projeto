import json
import unicodedata

# Função para normalizar texto Unicode
def normalize_unicode(text):
    # Normaliza o texto para o formato NFC
    normalized_text = unicodedata.normalize('NFC', text)
    return normalized_text

# Função para normalizar os valores no dataset
def normalize_and_clean_dataset(dataset):
    keys_to_remove = {'dre_key', 'in_force', 'conditional', 'processing', 'plain_text', 'pdf_error', 'timestamp'}
    
    if isinstance(dataset, dict):
        for key in keys_to_remove:
            if key in dataset:
                del dataset[key]
        for key, value in dataset.items():
            if isinstance(value, str):
                dataset[key] = normalize_unicode(value)
            elif isinstance(value, list):
                dataset[key] = [normalize_unicode(item) if isinstance(item, str) else item for item in value]
            elif isinstance(value, dict):
                dataset[key] = normalize_and_clean_dataset(value)
    elif isinstance(dataset, list):
        dataset = [normalize_and_clean_dataset(item) if isinstance(item, (dict, list)) else item for item in dataset]
    return dataset

# Carregar o dataset do arquivo JSON
with open('DREdataset.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Normalizar e limpar o dataset
normalized_cleaned_data = normalize_and_clean_dataset(data)

# Salvar o dataset normalizado e limpo de volta no arquivo JSON
with open('DREdataset_clean.json', 'w', encoding='utf-8') as file:
    json.dump(normalized_cleaned_data, file, ensure_ascii=False, indent=4)

print("Dataset normalizado e limpo salvo como 'DREdataset_normalized_cleaned.json'")
