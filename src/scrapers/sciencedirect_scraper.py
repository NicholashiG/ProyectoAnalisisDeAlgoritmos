import os
import sys
import time
import re  # Añadido para manejar expresiones regulares
import tempfile
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Añadir el directorio raíz al path para permitir importaciones absolutas
# cuando se ejecuta este script directamente
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

try:
    from src.drivers.web_driver import setup_driver, handle_cookie_dialog
except ImportError:
    # Si se ejecuta como script independiente, intentamos la importación relativa
    from ..drivers.web_driver import setup_driver, handle_cookie_dialog
    
def setup_driver_with_download_prefs(download_dir):
    """Configura el driver con preferencias de descarga"""
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_dir,
             "download.prompt_for_download": False,
             "download.directory_upgrade": True,
             "safebrowsing.enabled": False}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    return driver

def wait_for_manual_login(driver):
    """Espera a que el usuario inicie sesión manualmente"""
    print("\n=== INSTRUCCIONES PARA EL LOGIN MANUAL ===")
    print("1. Se abrirá el navegador en la página de ScienceDirect")
    print("2. Por favor, inicia sesión manualmente")
    print("3. Una vez que estés logueado, el script continuará automáticamente")
    print("4. El script esperará hasta que la URL contenga 'sciencedirect-com.crai'")
    print("===========================================\n")
    
    # Navegar a la página de login
    driver.get("https://login.crai.referencistas.com/login?url=https://www.sciencedirect.com")
    
    # Esperar hasta que se detecte que estamos en la página correcta después del login
    max_wait_time = 300  # 5 minutos máximo de espera
    start_time = time.time()
    
    print("Esperando a que completes el login manualmente...")
    
    while time.time() - start_time < max_wait_time:
        if "sciencedirect-com.crai" in driver.current_url:
            print("\n¡Login detectado correctamente!")
            print(f"URL actual: {driver.current_url}")
            time.sleep(2)  # Breve pausa para asegurar que la página está completamente cargada
            return True
        time.sleep(1)  # Revisar cada segundo
    
    print("Se agotó el tiempo de espera. Por favor, ejecuta el script nuevamente.")
    return False

def download_bibtex_from_page(driver, page_number, download_dir):
    """Descarga las citas BibTeX de una página de resultados"""
    offset = (page_number - 1) * 100  # Cada página muestra 100 resultados
    url = f"https://www-sciencedirect-com.crai.referencistas.com/search?qs=Computational%20Thinking&show=100&offset={offset}"
    
    print(f"Navegando a la página {page_number} (offset {offset})...")
    driver.get(url)
    
    try:
        # Esperar a que se carguen los resultados
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ResultItem"))
        )
        
        # Limpiar archivos .bib existentes en el directorio de descargas antes de exportar
        for file in os.listdir(download_dir):
            if file.endswith('.bib'):
                os.remove(os.path.join(download_dir, file))
                print(f"Limpiando archivo previo: {file}")
        
        # Instrucciones para selección manual
        print("\n=== SELECCIÓN MANUAL DE ARTÍCULOS ===")
        print("1. Ahora puedes seleccionar manualmente los artículos que deseas exportar")
        print("2. Marca los checkboxes de los artículos que te interesan")
        print("3. Cuando hayas terminado, presiona ENTER en la consola para continuar")
        print("===========================================\n")
        
        # Esperar a que el usuario seleccione los artículos
        input("Presiona ENTER cuando hayas seleccionado todos los artículos que deseas exportar...")
        
        # Hacer clic en el botón de exportar usando el selector específico
        export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'export-all-link-text') and text()='Export']"))
        )
        print("Haciendo clic en 'Export'...")
        export_button.click()
        
        # Hacer clic en "Export citation to BibTeX"
        bibtex_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Export citation to BibTeX')]"))
        )
        print("Exportando a BibTeX...")
        bibtex_option.click()
        
        # Esperar a que se complete la descarga (comprobar si aparece algún archivo .bib en la carpeta de descargas)
        timeout = 30
        start_time = time.time()
        downloaded = False
        
        while time.time() - start_time < timeout:
            # Verificar si hay algún archivo .bib en la carpeta de descargas
            bibtex_files = [f for f in os.listdir(download_dir) if f.endswith('.bib')]
            if bibtex_files:
                downloaded = True
                print(f"Archivo BibTeX descargado: {bibtex_files[0]}")
                # Dar tiempo para que termine de descargarse completamente
                time.sleep(3)  # Aumentado a 3 segundos para garantizar que se complete
                break
            time.sleep(1)
        
        if not downloaded:
            print("No se pudo confirmar la descarga del archivo BibTeX")
            return None
        
        # Obtener el nombre del archivo descargado
        bibtex_files = [f for f in os.listdir(download_dir) if f.endswith('.bib')]
        if not bibtex_files:
            return None
        
        # Renombramos el archivo descargado para incluir la página y evitar sobreescrituras
        original_path = os.path.join(download_dir, bibtex_files[0])
        new_filename = f"sciencedirect_page_{page_number}_{int(time.time())}.bib"
        new_path = os.path.join(download_dir, new_filename)
        
        # Usar shutil.copy2 en lugar de renombrar para evitar problemas con descargas en curso
        shutil.copy2(original_path, new_path)
        print(f"Archivo renombrado: {new_filename}")
        
        return new_path
        
    except Exception as e:
        print(f"Error al descargar BibTeX de la página {page_number}: {e}")
        return None

def combine_bibtex_files(file_paths, output_path):
    """Combina varios archivos BibTeX en uno solo, asegurando que no haya duplicados"""
    all_content = ""
    entry_ids = set()  # Para rastrear IDs ya procesadas
    
    print(f"Combinando {len(file_paths)} archivos BibTeX...")
    
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            print(f"Procesando: {os.path.basename(file_path)}")
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    
                    # Dividir el contenido en entradas individuales
                    entries = content.split('@')
                    
                    # Procesar cada entrada (excepto la primera que puede estar vacía)
                    for entry in entries:
                        if entry.strip():
                            # Reconstruir la entrada con el símbolo '@'
                            entry = '@' + entry
                            
                            # Extraer ID provisional de la entrada
                            entry_match = re.search(r'@\w+{([^,]+),', entry)
                            
                            if entry_match:
                                entry_id = entry_match.group(1)
                                
                                # Si la entrada no está duplicada, añadirla
                                if entry_id not in entry_ids:
                                    entry_ids.add(entry_id)
                                    all_content += entry + "\n\n"
            except Exception as e:
                print(f"Error al procesar archivo {file_path}: {e}")
    
    # Escribir el contenido combinado al archivo final
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(all_content)
    
    print(f"Archivos BibTeX combinados en: {output_path}")
    print(f"Total de entradas únicas: {len(entry_ids)}")

def fetch_data_from_sciencedirect(total_pages, output_file):
    """Extrae datos BibTeX de ScienceDirect para múltiples páginas"""
    # Crear directorio temporal para descargas
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Directorio temporal para descargas: {temp_dir}")
        
        # Inicializar el driver con las preferencias de descarga
        driver = setup_driver_with_download_prefs(temp_dir)
        
        try:
            # Esperar a que el usuario complete el login manualmente
            if not wait_for_manual_login(driver):
                print("No se detectó un login exitoso. Abortando.")
                return False
            
            # Descargar BibTeX de cada página
            bibtex_files = []
            for page in range(1, total_pages + 1):
                print(f"\n--- Procesando página {page} de {total_pages} ---")
                
                # Intentar hasta 3 veces la descarga por si hay problemas
                for attempt in range(3):
                    try:
                        bibtex_file = download_bibtex_from_page(driver, page, temp_dir)
                        if bibtex_file:
                            # Crear directorio de destino si no existe
                            os.makedirs(os.path.dirname(output_file), exist_ok=True)
                            
                            # Copiar archivo al directorio de destino con un nombre único
                            dest_file = f"sciencedirect_page_{page}.bib"
                            dest_path = os.path.join(os.path.dirname(output_file), dest_file)
                            
                            # Si ya existe un archivo con ese nombre, eliminarlo antes
                            if os.path.exists(dest_path):
                                os.remove(dest_path)
                                
                            shutil.copy2(bibtex_file, dest_path)
                            bibtex_files.append(dest_path)
                            print(f"Archivo guardado como: {dest_path}")
                            break  # Salir del bucle de intentos si se logró la descarga
                    except Exception as e:
                        print(f"Error en el intento {attempt+1}/3 para la página {page}: {e}")
                        if attempt == 2:  # Último intento
                            print(f"No se pudo descargar BibTeX para la página {page} después de 3 intentos")
                else:
                    # Este bloque se ejecuta si el bucle 'for' terminó normalmente (sin break)
                    print(f"No se pudo descargar BibTeX para la página {page}")
            
            # Combinar todos los archivos BibTeX en uno solo
            if bibtex_files:
                # Verificamos cada archivo antes de combinarlo
                valid_files = []
                for file_path in bibtex_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if '@' in content:  # Verificar que sea un archivo BibTeX válido
                                valid_files.append(file_path)
                            else:
                                print(f"Archivo descartado (no es BibTeX válido): {file_path}")
                    except Exception as e:
                        print(f"Error al leer archivo {file_path}: {e}")
                
                if valid_files:
                    combine_bibtex_files(valid_files, output_file)
                    print(f"Proceso completado. Archivo final: {output_file}")
                    return True
                else:
                    print("No se encontraron archivos BibTeX válidos para combinar.")
                    return False
            else:
                print("No se encontraron archivos BibTeX para combinar.")
                return False
                
        except Exception as e:
            print(f"Error durante la extracción de datos: {e}")
            return False
        finally:
            driver.quit()

if __name__ == "__main__":
    # Ejecutar como script independiente
    # Definir directorio para datos
    data_dir = os.path.join(ROOT_DIR, 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, 'sciencedirect_data.bib')
    
    print(f"Directorio para archivos de salida: {data_dir}")
    print("Iniciando extracción de datos desde ScienceDirect...")
    fetch_data_from_sciencedirect(total_pages=1, output_file=output_file)