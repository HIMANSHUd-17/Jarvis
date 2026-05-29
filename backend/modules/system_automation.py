"""
System command automation module
"""
import subprocess
import shlex
import os
from typing import Dict, List, Optional, Any
from core.logger import logger
from config.settings import ENABLE_SYSTEM_COMMANDS, ALLOWED_COMMANDS

class SystemAutomation:
    def __init__(self):
        self.enabled = ENABLE_SYSTEM_COMMANDS
        self.allowed_commands = ALLOWED_COMMANDS
        self.running_processes = {}
    
    def execute_command(self, command: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute system command safely
        
        Args:
            command: Command to execute (must be in ALLOWED_COMMANDS)
            args: Optional arguments for the command
        
        Returns:
            Result dictionary with status, output, and error
        """
        if not self.enabled:
            logger.warning("System commands are disabled")
            return {"success": False, "error": "System commands disabled"}
        
        command_lower = command.lower()
        
        if command_lower not in self.allowed_commands:
            logger.warning(f"Command not allowed: {command}")
            return {"success": False, "error": f"Command '{command}' not allowed"}
        
        try:
            cmd_map = {
                "chrome": self._open_chrome,
                "notepad": self._open_notepad,
                "explorer": self._open_explorer,
                "calculator": self._open_calculator,
                "vlc": self._open_vlc,
            }
            
            handler = cmd_map.get(command_lower)
            if handler:
                return handler(args)
            
            logger.error(f"No handler for command: {command}")
            return {"success": False, "error": "Command handler not found"}
        
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def _open_chrome(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Open Chrome browser"""
        try:
            url = args[0] if args else ""
            if url:
                subprocess.Popen(["chrome.exe", url])
                logger.info(f"Opened Chrome with URL: {url}")
                return {"success": True, "message": f"Chrome opened with {url}"}
            else:
                subprocess.Popen(["chrome.exe"])
                logger.info("Chrome opened")
                return {"success": True, "message": "Chrome opened"}
        except Exception as e:
            logger.error(f"Failed to open Chrome: {e}")
            return {"success": False, "error": str(e)}
    
    def _open_notepad(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Open Notepad"""
        try:
            subprocess.Popen(["notepad.exe"])
            logger.info("Notepad opened")
            return {"success": True, "message": "Notepad opened"}
        except Exception as e:
            logger.error(f"Failed to open Notepad: {e}")
            return {"success": False, "error": str(e)}
    
    def _open_explorer(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Open File Explorer"""
        try:
            path = args[0] if args else os.path.expanduser("~")
            subprocess.Popen(["explorer.exe", path])
            logger.info(f"File Explorer opened at: {path}")
            return {"success": True, "message": f"Explorer opened at {path}"}
        except Exception as e:
            logger.error(f"Failed to open Explorer: {e}")
            return {"success": False, "error": str(e)}
    
    def _open_calculator(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Open Calculator"""
        try:
            subprocess.Popen(["calc.exe"])
            logger.info("Calculator opened")
            return {"success": True, "message": "Calculator opened"}
        except Exception as e:
            logger.error(f"Failed to open Calculator: {e}")
            return {"success": False, "error": str(e)}
    
    def _open_vlc(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Open VLC media player"""
        try:
            vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
            if os.path.exists(vlc_path):
                subprocess.Popen([vlc_path])
                logger.info("VLC opened")
                return {"success": True, "message": "VLC opened"}
            else:
                return {"success": False, "error": "VLC not found"}
        except Exception as e:
            logger.error(f"Failed to open VLC: {e}")
            return {"success": False, "error": str(e)}
