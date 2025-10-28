import logging
import os
import re
import io
import requests
import base64
from utils.error import messageError
import uuid
import tempfile
import shutil


def clear_directory(directory):
    # Check if the directory exists
    if os.path.exists(directory):
        # Iterate over files in directory
        for file_name in os.listdir(directory):
            # Create the full path to the file
            file_path = os.path.join(directory, file_name)
            try:
                # Check if the item is a file
                if os.path.isfile(file_path):
                    # Delete the file
                    os.remove(file_path)
                # If it is a directory, recursively delete its contents
                elif os.path.isdir(file_path):
                    clear_directory(file_path)
            except Exception as e:
                logging.info(f"Could not delete {file_path}: {e}")
    else:
        logging.info(f"The directory {directory} does not exist")


def create_download_directory(directory_name):

    # Creates a directory for downloading files within the current working directory.

    # Args:
    #     directory_name (str): Name of the directory to be created.

    current_directory = os.getcwd()
    download_dir = os.path.join(current_directory, directory_name)
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def clean_filename(filename):
    # Defines a regular expression that matches any character that is not a letter, number, space, or underscore
    invalid_chars_regex = r'[^\w\s-]'
    # Replaces invalid characters with an empty string
    cleaned_filename = re.sub(invalid_chars_regex, '', filename)
    return cleaned_filename


def get_file(data):
    """ 
    Obtiene el contenido de un archivo, ya sea desde una URL, un binario o en Base64.

    :param data: URL del archivo, contenido binario o cadena Base64
    :return: Contenido binario del archivo, nombre del archivo y su extensión
    :raises MessageError: Si el formato de archivo no es válido
    """
    url_pattern = re.compile(r'^https?://\S+$')

    if isinstance(data, str) and url_pattern.match(data):
        # Si es una URL, obtiene el nombre y extensión del archivo
        try:
            response = requests.get(data, timeout=10)
            response.raise_for_status()  # Lanza error si el request falla

            # Obtener el nombre y la extensión desde la URL
            file_name = os.path.basename(data)
            if not file_name:  # Si no se obtiene el nombre del archivo, genera un ID único
                file_name = f"{uuid.uuid4()}.unknown"

            return response.content, file_name

        except requests.RequestException as e:
            raise messageError(f"Error al descargar el archivo: {e}")

    elif isinstance(data, (bytes, io.BytesIO)):
        # Si es binario, lo devuelve tal cual
        # Genera un nombre genérico para binarios
        file_name = f"{uuid.uuid4()}.bin"
        return data if isinstance(data, bytes) else data.getvalue(), file_name

    elif isinstance(data, str):
        # Si es una cadena, se asume que es Base64 y se decodifica
        try:
            # Intentamos decodificarlo como Base64
            decoded_data = base64.b64decode(data)
            file_name = f"{uuid.uuid4()}.pdf"  # Nombre genérico para Base64
            return decoded_data, file_name
        except Exception as e:
            raise messageError(f"Error al decodificar Base64: {e}")

    raise messageError("Formato de archivo desconocido")


def createTempFile(data, file_name):
    # Crear el archivo temporal con delete=False
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Escribir los datos en el archivo temporal
        temp_file.write(data)
        temp_file_path = temp_file.name

    # Renombrar el archivo temporal con el nombre especificado
    final_path = os.path.join(os.path.dirname(temp_file_path), file_name)
    # Mover y renombrar el archivo temporal
    shutil.move(temp_file_path, final_path)

    # Retorna la ruta del archivo renombrado
    return final_path
