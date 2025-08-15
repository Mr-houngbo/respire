def extract_ids_from_txt(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Retirer les parenthèses et les espaces inutiles
    content = content.strip('()\n ')
    
    # Séparer par virgule et convertir en liste d'entiers
    id_list = [int(x.strip()) for x in content.split(',') if x.strip().isdigit()]
    
    return id_list
