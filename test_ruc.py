#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de búsqueda de RUC
"""
import requests
from bs4 import BeautifulSoup

def test_buscar_ruc(ruc):
    """
    Función de prueba para buscar RUC en SUNAT
    """
    print(f"Buscando RUC: {ruc}")
    
    url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    try:
        # Primero obtenemos la página inicial para obtener el token
        session = requests.Session()
        initial_url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp'
        print("Obteniendo página inicial...")
        initial_response = session.get(initial_url, headers=headers, timeout=10)
        initial_response.raise_for_status()
        
        # Parsear la página inicial para obtener el token
        soup_initial = BeautifulSoup(initial_response.text, 'html.parser')
        token_input = soup_initial.find('input', {'name': 'token'})
        
        if not token_input:
            print("ERROR: No se pudo obtener el token de seguridad de SUNAT.")
            return None
        
        token = token_input.get('value', '')
        print(f"Token obtenido: {token[:20]}...")
        
        # Preparar los datos para el POST
        data = {
            'accion': 'consPorRuc',
            'nroRuc': ruc,
            'nrodoc': '',
            'razSoc': '',
            'token': token,
            'contexto': 'ti-it',
            'modo': '1',
            'search1': ruc,
            'codigo': '',
            'tipdoc': '1',
            'search2': '',
            'search3': '',
            'rbtnTipo': '1'
        }
        
        # Realizar la búsqueda
        print("Realizando búsqueda...")
        response = session.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parsear la respuesta
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la tabla con los resultados
        result_table = soup.find('table', class_='table')
        if not result_table:
            print("ERROR: No se encontraron datos para el RUC ingresado.")
            return None
        
        # Extraer la información de la tabla
        rows = result_table.find_all('tr')
        empresa_info = {}
        
        print("Información encontrada:")
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).replace(':', '').strip()
                value = cells[1].get_text(strip=True)
                print(f"  {label}: {value}")
                
                if 'RUC' in label:
                    empresa_info['ruc'] = value
                elif 'Razón Social' in label or 'Nombre Comercial' in label:
                    if 'razon_social' not in empresa_info:
                        empresa_info['razon_social'] = value
                elif 'Estado' in label:
                    empresa_info['estado'] = value
                elif 'Condición' in label:
                    empresa_info['condicion'] = value
                elif 'Dirección' in label:
                    empresa_info['direccion'] = value
        
        return empresa_info
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    # Probar con un RUC conocido (Telefónica del Perú)
    test_ruc = "20100017491"
    resultado = test_buscar_ruc(test_ruc)
    
    if resultado:
        print("\n" + "="*50)
        print("RESULTADO FINAL:")
        print("="*50)
        for key, value in resultado.items():
            print(f"{key}: {value}")
    else:
        print("\nNo se pudo obtener información.")
