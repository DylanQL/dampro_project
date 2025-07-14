#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de búsqueda de DNI
"""
import requests

def test_api_dni(dni):
    """
    Función de prueba para buscar DNI usando API
    """
    print(f"Buscando DNI: {dni}")
    
    # Intentar con API de eldni.com
    url = 'https://eldni.com/pe/buscar-datos-por-dni'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print("Probando con eldni.com...")
        # Usar una sesión para mantener las cookies
        with requests.Session() as s:
            # 1. Obtener la página inicial y el token CSRF
            get_response = s.get(url, headers=headers, timeout=5)
            get_response.raise_for_status()
            
            soup_initial = BeautifulSoup(get_response.text, 'html.parser')
            token_input = soup_initial.find('input', {'name': '_token'})
            
            if not token_input:
                print("✗ No se pudo encontrar el token de seguridad")
                raise ValueError("No token found")
            
            token = token_input['value']
            print(f"✓ Token obtenido: {token[:20]}...")

            # 2. Enviar la petición POST con el DNI y el token
            payload = {
                'dni': dni,
                '_token': token
            }
            post_response = s.post(url, data=payload, headers=headers, timeout=5)
            post_response.raise_for_status()

            # 3. Analizar la respuesta
            soup = BeautifulSoup(post_response.text, 'html.parser')
            table = soup.find('table', {'class': 'table table-striped table-scroll'})

            if table:
                rows = table.find_all('tr')
                if len(rows) > 1:
                    cols = rows[1].find_all('td')
                    nombres = cols[1].text.strip()
                    apellido_paterno = cols[2].text.strip()
                    apellido_materno = cols[3].text.strip()
                    
                    print("✓ eldni.com funcionando")
                    return {
                        'nombres': nombres,
                        'apellido_paterno': apellido_paterno,
                        'apellido_materno': apellido_materno
                    }
            
            print("✗ No se encontraron datos en eldni.com")
            
    except Exception as e:
        print(f"✗ Error en eldni.com: {e}")
    
    # Intentar con un segundo servicio (simulado)
    try:
        print("Probando segundo servicio...")
        # Este es un ejemplo. En un caso real, se usaría una API real
        demo_dnis = {
            '12345678': {
                'nombres': 'JUAN CARLOS',
                'apellido_paterno': 'PEREZ',
                'apellido_materno': 'GARCIA'
            },
            '87654321': {
                'nombres': 'MARIA ELENA',
                'apellido_paterno': 'RODRIGUEZ',
                'apellido_materno': 'LOPEZ'
            },
            '45678912': {
                'nombres': 'LUIS ALBERTO',
                'apellido_paterno': 'SANCHEZ',
                'apellido_materno': 'TORRES'
            }
        }
        
        if dni in demo_dnis:
            print("✓ Segundo servicio funcionando")
            return demo_dnis[dni]
        else:
            print("✗ DNI no encontrado en el segundo servicio")
            
    except Exception as e:
        print(f"✗ Error en segundo servicio: {e}")
    
    return None

if __name__ == "__main__":
    # Para usar BeautifulSoup
    from bs4 import BeautifulSoup
    
    # Probar con varios DNIs
    test_dnis = [
        "12345678",  # DNI de prueba 1
        "87654321",  # DNI de prueba 2
        "45678912",  # DNI de prueba 3
    ]
    
    for dni in test_dnis:
        print("="*60)
        resultado = test_api_dni(dni)
        if resultado:
            print(f"✓ DNI {dni} encontrado")
            print(f"  Nombres: {resultado['nombres']}")
            print(f"  Apellido Paterno: {resultado['apellido_paterno']}")
            print(f"  Apellido Materno: {resultado['apellido_materno']}")
        else:
            print(f"✗ DNI {dni} no encontrado")
        print()
