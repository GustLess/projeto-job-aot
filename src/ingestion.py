import requests
import pandas as pd

def fetch_aot_data():
    # URL da API do Array of Things (Projeto Chicago)
    url = "https://api.arrayofthings.org/api/observations?project=chicago"
    
    print(f"Conectando à API do AoT..." )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            observations = data.get('data', [])
            print(f"Sucesso! {len(observations)} observações encontradas.")
            
            # Converter para DataFrame para facilitar a visualização
            df = pd.json_normalize(observations)
            print("\nPrimeiras 5 linhas dos dados recebidos:")
            # Exibe as colunas principais: tempo, qual sensor e o valor medido
            print(df[['timestamp', 'sensor_path', 'value']].head())
            
            return df
        else:
            print(f"Erro na API: {response.status_code}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    fetch_aot_data()
