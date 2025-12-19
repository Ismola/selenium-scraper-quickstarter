"""
Pruebas para el archivo logging_config.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import tempfile
import logging
from datetime import datetime, timedelta
from utils.logging_config import (
    _clean_old_records_from_file, 
    _rotate_log_if_needed
)
from utils.config import LOG_FILE_DELETION_DAYS


def test_log_file_deletion_days_import():
    """Verifica que LOG_FILE_DELETION_DAYS se importa correctamente"""
    from utils.logging_config import LOG_FILE_DELETION_DAYS
    assert LOG_FILE_DELETION_DAYS == 30


def test_clean_old_records_from_file():
    """Prueba limpieza de registros antiguos"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        temp_path = temp_file.name
        
        current_date = datetime.now()
        old_date = current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 5)
        recent_date = current_date - timedelta(days=5)
        
        temp_file.write(f"{old_date.strftime('%Y-%m-%d %H:%M:%S')},123 - INFO - Antiguo\n")
        temp_file.write(f"{recent_date.strftime('%Y-%m-%d %H:%M:%S')},456 - INFO - Reciente\n")
        temp_file.write(f"{current_date.strftime('%Y-%m-%d %H:%M:%S')},789 - INFO - Actual\n")
    
    try:
        _clean_old_records_from_file(temp_path, current_date)
        
        with open(temp_path, 'r') as f:
            content = f.read()
        
        assert "Antiguo" not in content
        assert "Reciente" in content
        assert "Actual" in content
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_clean_old_records_removes_all_content_if_empty():
    """Prueba que elimina archivo si queda vacío"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        temp_path = temp_file.name
        
        current_date = datetime.now()
        old_date = current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 5)
        
        temp_file.write(f"{old_date.strftime('%Y-%m-%d %H:%M:%S')},123 - INFO - Solo antiguo\n")
    
    try:
        _clean_old_records_from_file(temp_path, current_date)
        
        # Si el archivo queda vacío, se elimina
        if os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                content = f.read().strip()
            assert content == "", "Archivo debe estar vacío"
        # Si se eliminó, también es correcto
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_rotate_log_if_needed_old_file():
    """Prueba que rotaciona si el archivo es muy antiguo"""
    with tempfile.TemporaryDirectory() as temp_dir:
        current_date = datetime.now()
        
        old_date = current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 5)
        old_log_filename = old_date.strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        old_log_path = os.path.join(temp_dir, old_log_filename)
        
        with open(old_log_path, 'w') as f:
            f.write(f"{old_date.strftime('%Y-%m-%d %H:%M:%S')},123 - INFO - Antiguo\n")
        
        import utils.logging_config as lc
        lc._current_log_file = old_log_path
        
        try:
            _rotate_log_if_needed(temp_dir, current_date)
            
            files = os.listdir(temp_dir)
            # Debe haber al menos 2 archivos (el antiguo + el nuevo)
            assert len(files) >= 2, f"Se debe haber creado nuevo archivo, hay {len(files)}"
            
            # El archivo antiguo debe seguir existiendo
            assert os.path.exists(old_log_path), "El archivo antiguo debe existir"
            
        finally:
            lc._current_log_file = None


def test_rotate_log_if_needed_recent_file():
    """Prueba que NO rotaciona si el archivo es reciente"""
    with tempfile.TemporaryDirectory() as temp_dir:
        current_date = datetime.now()
        
        recent_date = current_date - timedelta(days=5)
        recent_log_filename = recent_date.strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        recent_log_path = os.path.join(temp_dir, recent_log_filename)
        
        with open(recent_log_path, 'w') as f:
            f.write(f"{recent_date.strftime('%Y-%m-%d %H:%M:%S')},123 - INFO - Reciente\n")
        
        import utils.logging_config as lc
        lc._current_log_file = recent_log_path
        
        try:
            initial_count = len(os.listdir(temp_dir))
            _rotate_log_if_needed(temp_dir, current_date)
            final_count = len(os.listdir(temp_dir))
            
            assert initial_count == final_count, "No debe crear archivo si es reciente"
            
        finally:
            lc._current_log_file = None


def test_rotation_preserves_content():
    """Prueba que la rotación preserva contenido del archivo antiguo"""
    with tempfile.TemporaryDirectory() as temp_dir:
        current_date = datetime.now()
        
        old_date = current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 5)
        old_filename = old_date.strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        old_filepath = os.path.join(temp_dir, old_filename)
        
        test_content = "Contenido importante del archivo antiguo"
        with open(old_filepath, 'w') as f:
            f.write(f"{old_date.strftime('%Y-%m-%d %H:%M:%S')},000 - INFO - {test_content}\n")
        
        import utils.logging_config as lc
        lc._current_log_file = old_filepath
        
        try:
            _rotate_log_if_needed(temp_dir, current_date)
            
            with open(old_filepath, 'r') as f:
                content = f.read()
            
            assert test_content in content, "El contenido debe preservarse"
            
        finally:
            lc._current_log_file = None


def test_clean_preserves_recent_records():
    """Prueba que la limpieza preserva registros recientes"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        temp_path = temp_file.name
        
        current_date = datetime.now()
        
        # Crear registros en diferentes fechas
        dates_and_msgs = [
            (current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 10), "Muy antiguo"),
            (current_date - timedelta(days=LOG_FILE_DELETION_DAYS - 5), "Límite"),
            (current_date - timedelta(days=15), "Medio"),
            (current_date - timedelta(days=1), "Reciente"),
            (current_date, "Actual"),
        ]
        
        for date, msg in dates_and_msgs:
            temp_file.write(f"{date.strftime('%Y-%m-%d %H:%M:%S')},000 - INFO - {msg}\n")
        temp_file.close()
        
        try:
            _clean_old_records_from_file(temp_path, current_date)
            
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Los antiguos se eliminan
            assert "Muy antiguo" not in content, "Debe eliminar muy antiguos"
            
            # Los recientes se mantienen
            assert "Reciente" in content, "Debe mantener recientes"
            assert "Actual" in content, "Debe mantener actuales"
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def test_clean_multiple_files_scenario():
    """Prueba limpieza con múltiples archivos de diferentes edades"""
    with tempfile.TemporaryDirectory() as temp_dir:
        current_date = datetime.now()
        
        # Crear múltiples archivos
        scenarios = [
            ("ancient_old_records.log", current_date - timedelta(days=40), True),   # Antiguo, se elimina
            ("recent_old_records.log", current_date - timedelta(days=10), False),  # Reciente, se mantiene
            ("very_recent.log", current_date - timedelta(days=1), False),         # Muy reciente, se mantiene
        ]
        
        for filename, file_date, should_remove in scenarios:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                # Cada archivo tiene registros antiguos
                old_rec_date = current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 1)
                f.write(f"{old_rec_date.strftime('%Y-%m-%d %H:%M:%S')},000 - INFO - Old record\n")
                # Y registros recientes
                f.write(f"{current_date.strftime('%Y-%m-%d %H:%M:%S')},000 - INFO - Recent record\n")
        
        # Limpiar todos
        for filename, _, _ in scenarios:
            filepath = os.path.join(temp_dir, filename)
            _clean_old_records_from_file(filepath, current_date)
        
        # Verificar resultados
        remaining_files = os.listdir(temp_dir)
        
        for filename, file_date, should_remove in scenarios:
            filepath = os.path.join(temp_dir, filename)
            if filename == "ancient_old_records.log":
                # El archivo antiguo con solo registros viejos se debe eliminar
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        content = f.read().strip()
                    # Debería estar vacío o solo tener registros nuevos
                    assert "Old record" not in content, "Los registros antiguos deben eliminarse"
            else:
                # Los archivos recientes deben mantenerse
                assert os.path.exists(filepath), f"{filename} debe mantenerse"


def test_file_with_mixed_timestamps():
    """Prueba archivo con registros de diferentes timestamps"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        temp_path = temp_file.name
        
        current_date = datetime.now()
        
        # Registros intercalados
        records = [
            (current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 5), "Antiguo 1"),
            (current_date - timedelta(days=5), "Reciente 1"),
            (current_date - timedelta(days=LOG_FILE_DELETION_DAYS + 3), "Antiguo 2"),
            (current_date - timedelta(days=2), "Reciente 2"),
        ]
        
        for date, msg in records:
            temp_file.write(f"{date.strftime('%Y-%m-%d %H:%M:%S')},000 - INFO - {msg}\n")
        temp_file.close()
        
        try:
            _clean_old_records_from_file(temp_path, current_date)
            
            with open(temp_path, 'r') as f:
                content = f.read()
            
            assert "Antiguo 1" not in content
            assert "Antiguo 2" not in content
            assert "Reciente 1" in content
            assert "Reciente 2" in content
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
