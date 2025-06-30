#!/usr/bin/env python3
"""
Script de debug para analizar la página de SUNAT
"""
import requests
from bs4 import BeautifulSoup

def debug_sunat_page():
    """
    Función de debug para analizar la página de SUNAT
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        # Obtener la página inicial
        session = requests.Session()
        initial_url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp'
        print("Obteniendo página inicial...")
        response = session.get(initial_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content Length: {len(response.text)}")
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el token
        token_input = soup.find('input', {'name': 'token'})
        if token_input:
            token = token_input.get('value', '')
            print(f"Token encontrado: {token}")
        else:
            print("Token NO encontrado")
            
        # Buscar otros elementos importantes
        form = soup.find('form', {'id': 'form01'})
        if form:
            print("Formulario principal encontrado")
        else:
            print("Formulario principal NO encontrado")
            
        # Buscar campo RUC
        ruc_input = soup.find('input', {'id': 'txtRuc'})
        if ruc_input:
            print("Campo RUC encontrado")
        else:
            print("Campo RUC NO encontrado")
            
        # Guardar una muestra del HTML para análisis
        with open('/home/spikemm/Documentos/dampro_project/debug_sunat.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Página guardada como debug_sunat.html")
        
        return response.text
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    debug_sunat_page()
