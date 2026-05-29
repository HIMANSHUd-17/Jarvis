"""
Main WebSocket server for JARVIS
Handles real-time communication with frontend
"""
import asyncio
import json
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Set, Dict, Any
from core.logger import logger
from core.audio import AudioCapture, WakeWordDetector
from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.llm import LLMInterface
from modules.system_automation import SystemAutomation
from modules.whatsapp_automation import WhatsAppAutomation
from services.state_manager import StateManager, JarvisState
from config.settings import SERVER_HOST, SERVER_PORT, WEBSOCKET_MAX_SIZE, WEBSOCKET_PING_INTERVAL

class JarvisWebSocketServer:
    def __init__(self):
        self.clients: Set[WebSocketServerProtocol] = set()
        self.state_manager = StateManager()
        
        # Initialize components
        self.audio_capture = AudioCapture()
        self.wake_word_detector = WakeWordDetector(self.audio_capture)
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.llm = LLMInterface()
        self.system_automation = SystemAutomation()
        self.whatsapp = WhatsAppAutomation()
        
        # Start background tasks
        self.audio_listening = False
    
    async def start(self):
        """Start WebSocket server"""
        try:
            async with websockets.serve(
                self.handle_client,
                SERVER_HOST,
                SERVER_PORT,
                max_size=WEBSOCKET_MAX_SIZE,
                ping_interval=WEBSOCKET_PING_INTERVAL,
            ):
                logger.info(f"JARVIS WebSocket server started on ws://{SERVER_HOST}:{SERVER_PORT}")
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
            raise
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        # Send initial state
        await self.broadcast_state()
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {websocket.remote_address}")
        finally:
            self.clients.discard(websocket)
    
    async def process_message(self, websocket: WebSocketServerProtocol, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            command = data.get("command")
            
            if command == "get_state":
                await self.send_state(websocket)
            
            elif command == "start_listening":
                await self.start_listening()
            
            elif command == "stop_listening":
                await self.stop_listening()
            
            elif command == "send_text":
                user_input = data.get("input", "")
                await self.process_user_input(user_input)
            
            elif command == "execute_command":
                cmd = data.get("command_name", "")
                args = data.get("args", [])
                await self.execute_command(cmd, args)
            
            elif command == "send_whatsapp":
                contact = data.get("contact", "")
                msg = data.get("message", "")
                await self.send_whatsapp_message(contact, msg)
            
            elif command == "send_group_message":
                group = data.get("group", "")
                msg = data.get("message", "")
                await self.send_whatsapp_group_message(group, msg)
            
            else:
                logger.warning(f"Unknown command: {command}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def start_listening(self):
        """Start audio listening and wake word detection"""
        if self.audio_listening:
            return
        
        self.audio_listening = True
        self.state_manager.set_state(JarvisState.LISTENING)
        await self.broadcast_state()
        
        # Start audio capture
        audio_thread = asyncio.to_thread(self.audio_capture.start_listening)
        
        # Start wake word detection
        self.wake_word_detector.start(self.on_wake_word_detected)
        logger.info("Listening started")
    
    async def stop_listening(self):
        """Stop audio listening"""
        if not self.audio_listening:
            return
        
        self.audio_listening = False
        self.audio_capture.stop_listening()
        self.wake_word_detector.stop()
        
        self.state_manager.set_state(JarvisState.IDLE)
        await self.broadcast_state()
        logger.info("Listening stopped")
    
    async def on_wake_word_detected(self):
        """Callback when wake word is detected"""
        logger.info("Wake word detected - starting recording")
        self.state_manager.set_state(JarvisState.LISTENING)
        await self.broadcast_state()
        
        # Record and transcribe audio
        await asyncio.sleep(0.5)  # Small delay to avoid recording wake word
        user_input = await asyncio.to_thread(self.stt.record_and_transcribe, 10)
        
        if user_input:
            self.state_manager.last_user_input = user_input
            await self.process_user_input(user_input)
    
    async def process_user_input(self, user_input: str):
        """Process user input through LLM"""
        self.state_manager.set_state(JarvisState.PROCESSING)
        await self.broadcast_state()
        
        logger.info(f"Processing user input: {user_input}")
        
        try:
            # Generate LLM response
            llm_response = await asyncio.to_thread(
                self.llm.generate_response,
                user_input,
                self.state_manager.get_context()
            )
            
            self.state_manager.last_response = llm_response
            
            # Extract action if present
            action = llm_response.get("action")
            action_params = llm_response.get("action_params", {})
            response_text = llm_response.get("response", "")
            
            # Execute action if specified
            if action:
                await self.execute_action(action, action_params)
            
            # Speak response
            if response_text:
                self.state_manager.set_state(JarvisState.SPEAKING)
                await self.broadcast_state()
                
                await asyncio.to_thread(self.tts.speak, response_text, async_mode=False)
            
            # Broadcast response to all clients
            await self.broadcast_response({
                "input": user_input,
                "response": response_text,
                "action": action,
                "action_params": action_params
            })
            
            self.state_manager.set_state(JarvisState.IDLE)
            await self.broadcast_state()
        
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            self.state_manager.set_state(JarvisState.ERROR)
            await self.broadcast_state()
    
    async def execute_action(self, action: str, params: Dict[str, Any]):
        """Execute action specified by LLM"""
        logger.info(f"Executing action: {action} with params: {params}")
        
        if action == "execute_command":
            cmd = params.get("command", "")
            args = params.get("args", [])
            result = self.system_automation.execute_command(cmd, args)
            logger.info(f"Command result: {result}")
        
        elif action == "send_message":
            contact = params.get("contact", "")
            message = params.get("message", "")
            await self.send_whatsapp_message(contact, message)
    
    async def execute_command(self, command: str, args: list):
        """Execute system command"""
        result = self.system_automation.execute_command(command, args)
        
        response_text = result.get("message") or result.get("error")
        self.tts.speak(response_text)
        
        await self.broadcast_response({
            "type": "command_result",
            "command": command,
            "result": result
        })
    
    async def send_whatsapp_message(self, contact: str, message: str):
        """Send WhatsApp message"""
        try:
            result = await self.whatsapp.send_message(contact, message)
            logger.info(f"WhatsApp message result: {result}")
            await self.broadcast_response({
                "type": "whatsapp_result",
                "result": result
            })
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
    
    async def send_whatsapp_group_message(self, group: str, message: str):
        """Send WhatsApp group message"""
        try:
            result = await self.whatsapp.send_group_message(group, message)
            logger.info(f"WhatsApp group message result: {result}")
            await self.broadcast_response({
                "type": "whatsapp_result",
                "result": result
            })
        except Exception as e:
            logger.error(f"Error sending WhatsApp group message: {e}")
    
    async def broadcast_state(self):
        """Broadcast current state to all connected clients"""
        state_data = {
            "type": "state_update",
            "data": self.state_manager.to_dict()
        }
        
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(state_data)) for client in self.clients],
                return_exceptions=True
            )
    
    async def send_state(self, websocket: WebSocketServerProtocol):
        """Send current state to a specific client"""
        state_data = {
            "type": "state_update",
            "data": self.state_manager.to_dict()
        }
        await websocket.send(json.dumps(state_data))
    
    async def broadcast_response(self, response: Dict[str, Any]):
        """Broadcast response to all clients"""
        response_data = {
            "type": "response",
            "data": response
        }
        
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(response_data)) for client in self.clients],
                return_exceptions=True
            )

async def main():
    """Main entry point"""
    server = JarvisWebSocketServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
