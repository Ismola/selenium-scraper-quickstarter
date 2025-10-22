import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils.streaming_service import streaming_service
from actions.web_driver import get_page, close_driver, get_wait
from utils.config import STREAMING_ENABLED


def streaming_demo_controller():
    """
    Ejemplo de controller que integra streaming para mostrar 
    una automatización de búsqueda en Google en tiempo real
    """
    driver = None
    
    try:
        logging.info("Iniciando demostración con streaming")
        
        # Iniciar navegador
        driver = get_page(browser='chrome', url='https://www.google.com')
        wait = get_wait(driver)
        
        # Configurar streaming si está habilitado
        if STREAMING_ENABLED and streaming_service.is_streaming():
            streaming_service.set_driver(driver)
            logging.info("Driver configurado para streaming")
        
        # Pausa para que se vea la página inicial
        time.sleep(2)
        
        # Paso 1: Buscar campo de búsqueda
        logging.info("Buscando campo de búsqueda...")
        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # Destacar elemento si hay streaming
        if streaming_service.is_streaming():
            frame = streaming_service.capture_frame_with_element_highlight(
                (By.NAME, "q")
            )
            time.sleep(1)  # Pausa para ver el destacado
        
        # Paso 2: Escribir texto de búsqueda
        search_text = "Selenium WebDriver Python"
        logging.info(f"Escribiendo texto: {search_text}")
        search_box.clear()
        
        # Escribir letra por letra para efecto visual
        for char in search_text:
            search_box.send_keys(char)
            time.sleep(0.1)  # Pausa entre caracteres
        
        time.sleep(1)
        
        # Paso 3: Hacer clic en el botón de búsqueda
        logging.info("Haciendo clic en buscar...")
        search_button = driver.find_element(By.NAME, "btnK")
        
        # Destacar botón de búsqueda
        if streaming_service.is_streaming():
            frame = streaming_service.capture_frame_with_element_highlight(
                (By.NAME, "btnK")
            )
            time.sleep(1)
        
        search_button.click()
        
        # Paso 4: Esperar resultados
        logging.info("Esperando resultados...")
        wait.until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        time.sleep(2)
        
        # Paso 5: Scroll para mostrar más resultados
        logging.info("Haciendo scroll en resultados...")
        for i in range(3):
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(1)
        
        # Paso 6: Hacer clic en el primer resultado
        logging.info("Haciendo clic en primer resultado...")
        first_result = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "h3"))
        )
        
        # Destacar primer resultado
        if streaming_service.is_streaming():
            frame = streaming_service.capture_frame_with_element_highlight(
                (By.CSS_SELECTOR, "h3")
            )
            time.sleep(1)
        
        first_result.click()
        
        # Paso 7: Esperar a que cargue la nueva página
        time.sleep(3)
        
        # Obtener información final
        current_url = driver.current_url
        page_title = driver.title
        
        logging.info(f"Demostración completada. URL final: {current_url}")
        
        return {
            "success": True,
            "message": "Demostración de streaming completada exitosamente",
            "data": {
                "search_text": search_text,
                "final_url": current_url,
                "page_title": page_title,
                "streaming_active": streaming_service.is_streaming()
            }
        }
        
    except Exception as e:
        logging.error(f"Error en demostración de streaming: {e}")
        return {
            "success": False,
            "message": f"Error en demostración: {str(e)}",
            "error": "DEMO_ERROR"
        }
        
    finally:
        # Limpiar recursos
        if driver and not streaming_service.is_streaming():
            # Solo cerrar driver si no hay streaming activo
            close_driver(driver)


def interactive_streaming_controller():
    """
    Controller para una sesión interactiva donde el usuario 
    puede controlar el navegador a través de la API web
    """
    try:
        if not STREAMING_ENABLED:
            return {
                "success": False,
                "message": "Streaming debe estar habilitado para sesiones interactivas",
                "error": "STREAMING_DISABLED"
            }
        
        if not streaming_service.is_streaming():
            return {
                "success": False,
                "message": "Debe iniciar streaming primero",
                "error": "NO_ACTIVE_STREAM"
            }
        
        # Verificar que tenemos un driver activo
        if not streaming_service.driver:
            return {
                "success": False,
                "message": "No hay navegador activo",
                "error": "NO_ACTIVE_BROWSER"
            }
        
        current_url = streaming_service.driver.current_url
        page_title = streaming_service.driver.title
        
        return {
            "success": True,
            "message": "Sesión interactiva lista",
            "data": {
                "current_url": current_url,
                "page_title": page_title,
                "stream_info": streaming_service.get_stream_info(),
                "instructions": {
                    "navigate": "POST /stream/navigate con {'url': 'https://example.com'}",
                    "click": "POST /stream/action con {'action_type': 'click', 'locator': 'id', 'value': 'element-id'}",
                    "type": "POST /stream/action con {'action_type': 'type', 'locator': 'name', 'value': 'input-name', 'text': 'texto'}",
                    "scroll": "POST /stream/action con {'action_type': 'scroll', 'x': 0, 'y': 500}",
                    "script": "POST /stream/action con {'action_type': 'execute_script', 'script': 'código JavaScript'}"
                }
            }
        }
        
    except Exception as e:
        logging.error(f"Error en sesión interactiva: {e}")
        return {
            "success": False,
            "message": f"Error en sesión interactiva: {str(e)}",
            "error": "INTERACTIVE_ERROR"
        }


def streaming_scraping_demo_controller():
    """
    Demostración de scraping con streaming para mostrar 
    extracción de datos en tiempo real
    """
    driver = None
    
    try:
        logging.info("Iniciando demostración de scraping con streaming")
        
        # Navegar a una página con datos para scrapear
        driver = get_page(browser='chrome', url='https://quotes.toscrape.com/')
        wait = get_wait(driver)
        
        # Configurar streaming
        if STREAMING_ENABLED and streaming_service.is_streaming():
            streaming_service.set_driver(driver)
        
        time.sleep(2)
        
        # Scrapear todas las citas
        quotes_data = []
        
        # Encontrar todas las citas
        quotes = driver.find_elements(By.CLASS_NAME, "quote")
        logging.info(f"Encontradas {len(quotes)} citas para scrapear")
        
        for i, quote in enumerate(quotes):
            try:
                # Destacar cita actual
                if streaming_service.is_streaming():
                    driver.execute_script(
                        "arguments[0].style.border='3px solid green'; arguments[0].style.backgroundColor='#f0f8ff';",
                        quote
                    )
                    time.sleep(1)
                
                # Extraer datos
                text = quote.find_element(By.CLASS_NAME, "text").text
                author = quote.find_element(By.CLASS_NAME, "author").text
                tags_elements = quote.find_elements(By.CLASS_NAME, "tag")
                tags = [tag.text for tag in tags_elements]
                
                quote_data = {
                    "index": i + 1,
                    "text": text,
                    "author": author,
                    "tags": tags
                }
                
                quotes_data.append(quote_data)
                logging.info(f"Scraped quote {i + 1}: {author}")
                
                # Remover destacado
                driver.execute_script(
                    "arguments[0].style.border=''; arguments[0].style.backgroundColor='';",
                    quote
                )
                
                time.sleep(0.5)
                
            except Exception as e:
                logging.warning(f"Error scraping quote {i + 1}: {e}")
                continue
        
        # Scroll y navegar a siguiente página si existe
        try:
            next_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Next")
            
            # Destacar botón siguiente
            if streaming_service.is_streaming():
                frame = streaming_service.capture_frame_with_element_highlight(
                    (By.PARTIAL_LINK_TEXT, "Next")
                )
                time.sleep(1)
            
            next_button.click()
            time.sleep(2)
            
            # Scrapear primera cita de la siguiente página
            if driver.find_elements(By.CLASS_NAME, "quote"):
                first_quote = driver.find_element(By.CLASS_NAME, "quote")
                if streaming_service.is_streaming():
                    frame = streaming_service.capture_frame_with_element_highlight(
                        (By.CLASS_NAME, "quote")
                    )
                    time.sleep(1)
        
        except:
            logging.info("No hay página siguiente o botón no encontrado")
        
        return {
            "success": True,
            "message": f"Scraping completado exitosamente. {len(quotes_data)} citas extraídas",
            "data": {
                "quotes_count": len(quotes_data),
                "quotes": quotes_data[:3],  # Solo primeras 3 para no sobrecargar
                "total_quotes_scraped": len(quotes_data),
                "streaming_active": streaming_service.is_streaming()
            }
        }
        
    except Exception as e:
        logging.error(f"Error en demostración de scraping: {e}")
        return {
            "success": False,
            "message": f"Error en scraping demo: {str(e)}",
            "error": "SCRAPING_DEMO_ERROR"
        }
        
    finally:
        if driver and not streaming_service.is_streaming():
            close_driver(driver)