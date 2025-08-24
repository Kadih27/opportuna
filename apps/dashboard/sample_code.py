import pandas as pd
import random
import string

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

data = {
    'title': ['Développeur Fullstack', 'Data Analyst'],
    'type': ['Full Time', 'Part Time'],
    'location': ['Paris', 'Lyon'],
    'description': [
        'Développement d\'une application web avec Django et React.',
        'Analyse de données clients et création de rapports.'
    ],
    'requirement': [
        'BAC+4 en informatique, maîtrise de Python et JavaScript',
        'Compétences en SQL et Python (Pandas)'
    ],
    'category': ['IT', 'Data'],
    'salary': ['1200', '1100'],
    'deadline': ['2025-06-30', '2025-07-15'],
    'other_information': ["Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s",
                          "It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
                          ]
}

random_str = generate_random_string(12)

df = pd.DataFrame(data)
df.to_excel(f'exemple_offres{random_str}.xlsx', index=False)