"""Connector registry."""

from src.integrations.connectors.browser_connector import BrowserConnector
from src.integrations.connectors.calendar_connector import CalendarConnector
from src.integrations.connectors.gmail_connector import GmailConnector
from src.integrations.connectors.git_connector import GitConnector
from src.integrations.connectors.health_connector import HealthConnector
from src.integrations.connectors.notion_connector import NotionConnector
from src.integrations.connectors.obsidian_connector import ObsidianConnector
from src.integrations.connectors.rss_connector import RSSConnector
from src.integrations.connectors.whatsapp_connector import WhatsAppConnector


def available_connectors() -> dict:
    connectors = [
        GmailConnector,
        CalendarConnector,
        NotionConnector,
        BrowserConnector,
        HealthConnector,
        ObsidianConnector,
        GitConnector,
        WhatsAppConnector,
        RSSConnector,
    ]
    return {connector.id: connector for connector in connectors}
