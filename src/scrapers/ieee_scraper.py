from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

from src.drivers.web_driver import setup_driver


def fetch_data_from_ieee(pages: int = 1):
    """Extrae datos de IEEE Xplore con paginación mejorada"""
    driver = setup_driver()
    all_data = []

    try:
        # Paso 1: Acceder a IEEE Xplore
        print("Accediendo a IEEE Xplore...")
        driver.get(
            "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=computational%20thinking")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )

        handle_cookie_dialog(driver)
        time.sleep(3)

        # Paso 3: Extraer artículos con paginación robusta
        current_page = 1
        while current_page <= pages:
            print(f"\nProcesando página {current_page}...")

            try:
                # Esperar a que carguen los resultados
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.List-results-items, xpl-results-item"))
                )

                # Obtener artículos
                articles = driver.find_elements(By.CSS_SELECTOR,
                                                "div.List-results-items div.List-row, xpl-results-item")
                if not articles:
                    articles = driver.find_elements(By.CSS_SELECTOR, "div.result-item")

                print(f"Encontrados {len(articles)} artículos en esta página")

                if not articles:
                    print("No se encontraron artículos. Verificando si hay mensaje de error...")
                    try:
                        error_msg = driver.find_element(By.CSS_SELECTOR, "div.alert-message").text
                        print(f"Mensaje de error: {error_msg}")
                        break
                    except:
                        print("No se encontró mensaje de error visible")
                        break

                # Procesar artículos
                for idx, article in enumerate(articles, 1):
                    try:
                        print(f"\nProcesando artículo {idx}/{len(articles)}...")

                        # Scroll al artículo
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", article)
                        time.sleep(0.5)

                        # Extraer datos básicos
                        title = article.find_element(By.CSS_SELECTOR,
                                                     "h2 a, h3 a, [data-testid='document-title']").text.strip()
                        authors = ", ".join([a.text for a in article.find_elements(By.CSS_SELECTOR,
                                                                                   "span.author, a[data-testid='author-name']")])

                        try:
                            year_text = article.find_element(By.CSS_SELECTOR,
                                                             "div.description, div.publisher-info-container").text
                            year = re.search(r'(19|20)\d{2}', year_text).group(0)
                        except:
                            year = ""

                        # Extraer abstract completo
                        abstract = "No abstract available"
                        try:
                            article_link = article.find_element(By.CSS_SELECTOR, "h2 a, h3 a")
                            article_url = article_link.get_attribute("href")

                            # Abrir en nueva pestaña
                            driver.execute_script("window.open(arguments[0]);", article_url)
                            driver.switch_to.window(driver.window_handles[-1])
                            time.sleep(3)

                            # Extraer abstract con múltiples intentos
                            abstract_selectors = [
                                "div.abstract-text div",
                                "div.abstract-text",
                                "section.abstract",
                                "div.u-mb-1",
                                "div.AbstractContainer"
                            ]

                            for selector in abstract_selectors:
                                try:
                                    abstract_element = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                    )
                                    abstract = abstract_element.text.strip()
                                    if abstract and abstract.lower() not in ["no abstract available", "..."]:
                                        break
                                except:
                                    continue

                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            time.sleep(1)
                        except Exception as e:
                            print(f"Error al extraer abstract completo: {e}")

                        # Guardar datos
                        all_data.append({
                            'title': title,
                            'author': authors,
                            'year': year,
                            'abstract': abstract
                        })

                        print(f"✓ Artículo procesado: {title[:50]}...")

                    except Exception as e:
                        print(f"✗ Error procesando artículo {idx}: {e}")
                        continue

                # Navegar a siguiente página
                if current_page < pages:
                    print(f"\nIntentando navegar a página {current_page + 1}...")
                    try:
                        # Primero intentar con el botón de siguiente
                        next_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, "a[aria-label='Next page'], button[aria-label='Next Page']"))
                        )
                        next_btn.click()
                        time.sleep(5)

                        # Verificar que realmente cambió de página
                        WebDriverWait(driver, 10).until(
                            lambda d: "pageNumber=" + str(current_page + 1) in d.current_url
                        )
                        current_page += 1

                    except Exception as e:
                        print(f"No se pudo navegar a la página {current_page + 1}. Intentando método alternativo...")
                        try:
                            # Método alternativo: construir URL directamente
                            next_page_url = re.sub(r'pageNumber=\d+', f'pageNumber={current_page + 1}',
                                                   driver.current_url)
                            if "pageNumber=" not in next_page_url:
                                next_page_url = f"{driver.current_url}&pageNumber={current_page + 1}"

                            driver.get(next_page_url)
                            time.sleep(5)

                            # Verificar que cargó la nueva página
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "div.List-results-items, xpl-results-item"))
                            )
                            current_page += 1

                        except Exception as alt_e:
                            print(f"Error en método alternativo de paginación: {alt_e}")
                            print("No se pudo avanzar a la siguiente página. Terminando extracción.")
                            break
                else:
                    break

            except Exception as page_e:
                print(f"Error al procesar página {current_page}: {page_e}")
                break

        return all_data

    except Exception as e:
        print(f"Error general durante la extracción: {e}")
        return all_data
    finally:
        driver.quit()
        print("\nExtracción completada. Cerrando navegador.")

def handle_cookie_dialog(driver):
    """Maneja el diálogo de cookies si aparece"""
    try:
        # Intentar con selector moderno primero
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Accept all cookies']"))
        )
        cookie_button.click()
        print("Diálogo de cookies aceptado")
        time.sleep(1)
        return True
    except:
        print("No se encontró diálogo de cookies o ya fue aceptado")
        return False