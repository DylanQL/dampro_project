#!/usr/bin/env python3
"""
Script de prueba para verificar la nueva funcionalidad de búsqueda de RUC
"""
import requests

def test_api_ruc(ruc):
    """
    Función de prueba para buscar RUC usando API
    """
    print(f"Buscando RUC: {ruc}")
    
    # Primer servicio
    url = f'https://dniruc.apisperu.com/api/v1/ruc/{ruc}?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InJpenF1ZUBob3RtYWlsLmNvbSJ9.s3_Cf11HMC9J20aU9nLUApd7Rz5_E-4iIssjOSKWU_I'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
    }

    try:
        print("Probando primer servicio...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"Respuesta del primer servicio: {data}")
        
        if data.get('success') and 'razonSocial' in data:
            print("✓ Primer servicio funcionando")
            return data
        else:
            print("✗ Primer servicio no retornó datos válidos")
            
    except Exception as e:
        print(f"✗ Error en primer servicio: {e}")
    
    # Segundo servicio
    try:
        print("Probando segundo servicio...")
        backup_url = f'https://api.apis.net.pe/v1/ruc?numero={ruc}'
        backup_response = requests.get(backup_url, headers=headers, timeout=10)
        backup_response.raise_for_status()
        
        backup_data = backup_response.json()
        print(f"Respuesta del segundo servicio: {backup_data}")
        
        if backup_data and 'nombre' in backup_data:
            print("✓ Segundo servicio funcionando")
            return backup_data
        else:
            print("✗ Segundo servicio no retornó datos válidos")
            
    except Exception as e:
        print(f"✗ Error en segundo servicio: {e}")
    
    return None

if __name__ == "__main__":
    # Probar con varios RUCs conocidos
    test_rucs = [
        "20100017491",  # Telefónica del Perú
        "20131312955",  # Saga Falabella
        "20100070970",  # Supermercados Peruanos S.A.
    ]
    
    for ruc in test_rucs:
        print("="*60)
        resultado = test_api_ruc(ruc)
        if resultado:
            print(f"✓ RUC {ruc} encontrado")
            if 'razonSocial' in resultado:
                print(f"  Razón Social: {resultado['razonSocial']}")
            elif 'nombre' in resultado:
                print(f"  Nombre: {resultado['nombre']}")
        else:
            print(f"✗ RUC {ruc} no encontrado")
        print()
