"""
WhatsApp automation module using Playwright for headless browser control
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from core.logger import logger
from config.settings import WHATSAPP_HEADLESS, WHATSAPP_TIMEOUT, WHATSAPP_CONTACTS_FILE

class WhatsAppAutomation:
    def __init__(self):
        self.headless = WHATSAPP_HEADLESS
        self.timeout = WHATSAPP_TIMEOUT
        self.contacts_file = WHATSAPP_CONTACTS_FILE
        self.browser = None
        self.page = None
        self.contacts = self._load_contacts()
    
    def _load_contacts(self) -> Dict[str, str]:
        """Load contacts from JSON file"""
        try:
            if Path(self.contacts_file).exists():
                with open(self.contacts_file, 'r') as f:
                    data = json.load(f)
                    contacts = {}
                    for contact in data.get("contacts", []):
                        contacts[contact["name"].lower()] = contact["phone"]
                    logger.info(f"Loaded {len(contacts)} contacts")
                    return contacts
        except Exception as e:
            logger.error(f"Error loading contacts: {e}")
        return {}
    
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=["--start-maximized"]
            )
            
            context = await self.browser.new_context(no_viewport=True)
            self.page = await context.new_page()
            
            logger.info("WhatsApp Playwright browser initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            return False
    
    async def open_whatsapp(self) -> bool:
        """Open WhatsApp Web"""
        try:
            if not self.page:
                return False
            
            await self.page.goto("https://web.whatsapp.com", timeout=self.timeout * 1000)
            logger.info("WhatsApp Web opened")
            
            # Wait for QR code or chat list to load
            try:
                await self.page.wait_for_selector("[data-testid='chat-list']", timeout=30000)
                logger.info("WhatsApp authenticated")
                return True
            except:
                logger.warning("QR code scan required for WhatsApp authentication")
                return False
        
        except Exception as e:
            logger.error(f"Error opening WhatsApp: {e}")
            return False
    
    async def send_message(self, contact_name: str, message: str) -> Dict[str, Any]:
        """
        Send message to a WhatsApp contact
        
        Args:
            contact_name: Name of contact to message
            message: Message to send
        
        Returns:
            Result dictionary
        """
        try:
            if not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            contact_phone = self.contacts.get(contact_name.lower())
            if not contact_phone:
                return {"success": False, "error": f"Contact '{contact_name}' not found"}
            
            # Navigate to chat link
            whatsapp_url = f"https://web.whatsapp.com/send?phone={contact_phone}"
            await self.page.goto(whatsapp_url, timeout=self.timeout * 1000)
            
            # Wait for message input field
            await self.page.wait_for_selector("[data-testid='msg-input']", timeout=self.timeout * 1000)
            
            # Type message
            await self.page.fill("[data-testid='msg-input']", message)
            
            # Send message (press Enter)
            await self.page.press("[data-testid='msg-input']", "Enter")
            
            logger.info(f"Message sent to {contact_name}: {message[:50]}...")
            return {
                "success": True,
                "message": f"Message sent to {contact_name}",
                "contact": contact_name,
                "text": message
            }
        
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_group_message(self, group_name: str, message: str) -> Dict[str, Any]:
        """Send message to a WhatsApp group"""
        try:
            if not self.page:
                return {"success": False, "error": "Browser not initialized"}
            
            # Open search
            await self.page.click("[data-testid='chat-list-search-input']")
            await self.page.fill("[data-testid='chat-list-search-input']", group_name)
            
            # Wait and click group
            await self.page.wait_for_selector("[data-testid='chat-list-item']", timeout=5000)
            await self.page.click("[data-testid='chat-list-item']")
            
            # Wait for message input
            await self.page.wait_for_selector("[data-testid='msg-input']", timeout=self.timeout * 1000)
            
            # Type and send message
            await self.page.fill("[data-testid='msg-input']", message)
            await self.page.press("[data-testid='msg-input']", "Enter")
            
            logger.info(f"Group message sent to {group_name}: {message[:50]}...")
            return {
                "success": True,
                "message": f"Message sent to group {group_name}",
                "group": group_name,
                "text": message
            }
        
        except Exception as e:
            logger.error(f"Error sending group message: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close browser"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("WhatsApp automation closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
