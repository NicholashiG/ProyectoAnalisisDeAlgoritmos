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
    # Aumentar el tamaño de la ventana para evitar problemas con elementos responsive
    options.add_argument("--window-size=1920,1080")
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


def login_to_university_portal(driver, username, password):
    """Inicia sesión en el portal de la Universidad del Quindío"""
    try:
        print("Intentando iniciar sesión en el portal universitario...")
        # Esperar a que aparezca el campo de usuario
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(username)

        # Completar campo de contraseña
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)

        # Hacer clic en el botón de inicio de sesión
        login_button = driver.find_element(By.NAME, "submit")
        login_button.click()

        # Esperar a que la página se cargue después del inicio de sesión
        WebDriverWait(driver, 10).until(
            EC.url_changes(driver.current_url)
        )

        print("Inicio de sesión exitoso")
        return True
    except Exception as e:
        print(f"Error durante el inicio de sesión: {e}")
        return False


def navigate_to_database(driver, database_name):
    """Navega a la base de datos específica desde el portal universitario"""
    try:
        # Navegar a la sección de bases de datos
        print(f"Navegando a la base de datos: {database_name}...")

        # Esperar a que aparezca el enlace a las bases de datos
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Bases de datos"))
        ).click()

        # Buscar y hacer clic en el enlace a la base de datos específica
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, database_name))
        ).click()

        # Esperar a que se complete la redirección
        time.sleep(5)

        # Si hay varias ventanas abiertas, cambiar a la última (nueva)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])

        print(f"Navegación a {database_name} exitosa")
        return True
    except Exception as e:
        print(f"Error al navegar a la base de datos: {e}")
        return False