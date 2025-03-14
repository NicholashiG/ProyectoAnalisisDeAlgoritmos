from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def setup_driver():
    """Configura y devuelve un driver de Chrome para Selenium"""
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # Añadir opciones para mejorar el rendimiento
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def handle_cookie_dialog(driver):
    """Maneja el diálogo de cookies intentando aceptar todas las cookies"""
    try:
        # Esperar hasta 5 segundos para que aparezca el diálogo de cookies
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        # Hacer clic en el botón "Allow all cookies"
        cookie_button.click()
        print("Cookies aceptadas exitosamente")
        # Breve pausa para permitir que la página se actualice
        time.sleep(1)
        return True
    except (TimeoutException, NoSuchElementException) as e:
        print("No se encontró el diálogo de cookies o ya fue aceptado")
        return False