"""
State management for JARVIS backend
"""
from enum import Enum
from typing import Dict, Any
from datetime import datetime
import json

class JarvisState(Enum):
    """JARVIS operational states"""
    IDLE = "Idle"
    LISTENING = "Listening"
    PROCESSING = "Processing"
    SPEAKING = "Speaking"
    ERROR = "Error"

class StateManager:
    def __init__(self):
        self.current_state = JarvisState.IDLE
        self.state_history = []
        self.context = {}
        self.last_user_input = None
        self.last_response = None
    
    def set_state(self, new_state: JarvisState, context: Dict[str, Any] = None):
        """Update current state"""
        old_state = self.current_state
        self.current_state = new_state
        
        state_change = {
            "timestamp": datetime.now().isoformat(),
            "from": old_state.value,
            "to": new_state.value,
            "context": context or {}
        }
        self.state_history.append(state_change)
        
        if len(self.state_history) > 100:  # Keep last 100 state changes
            self.state_history = self.state_history[-100:]
    
    def get_state(self) -> str:
        """Get current state value"""
        return self.current_state.value
    
    def update_context(self, **kwargs):
        """Update context information"""
        self.context.update(kwargs)
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization"""
        return {
            "state": self.current_state.value,
            "context": self.context,
            "last_user_input": self.last_user_input,
            "last_response": self.last_response,
            "timestamp": datetime.now().isoformat()
        }
