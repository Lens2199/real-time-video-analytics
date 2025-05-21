import logging
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all agents in the system
    """
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize the base agent
        
        Args:
            agent_id (str): Unique ID for this agent
            agent_type (str): Type of agent
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = {}
        self.connected_agents = []
        logger.info(f"Initialized {agent_type} agent with ID: {agent_id}")
    
    def connect(self, agent):
        """
        Connect to another agent
        
        Args:
            agent: Agent to connect to
        """
        if agent not in self.connected_agents:
            self.connected_agents.append(agent)
            # Two-way connection
            if self not in agent.connected_agents:
                agent.connect(self)
            
            logger.debug(f"Agent {self.agent_id} connected to agent {agent.agent_id}")
    
    def send_message(self, recipient_id: str, message_type: str, content: Any) -> bool:
        """
        Send a message to another agent
        
        Args:
            recipient_id (str): ID of the recipient agent
            message_type (str): Type of message
            content (Any): Message content
            
        Returns:
            bool: True if message was delivered, False otherwise
        """
        # Find the recipient agent
        recipient = None
        for agent in self.connected_agents:
            if agent.agent_id == recipient_id:
                recipient = agent
                break
        
        if recipient:
            # Deliver the message
            return recipient.receive_message(self.agent_id, message_type, content)
        else:
            logger.warning(f"Agent {self.agent_id} tried to send message to unknown agent {recipient_id}")
            return False
    
    def receive_message(self, sender_id: str, message_type: str, content: Any) -> bool:
        """
        Receive a message from another agent
        
        Args:
            sender_id (str): ID of the sender agent
            message_type (str): Type of message
            content (Any): Message content
            
        Returns:
            bool: True if message was processed, False otherwise
        """
        logger.debug(f"Agent {self.agent_id} received {message_type} message from {sender_id}")
        
        # Default implementation just logs the message
        return True
    
    def broadcast(self, message_type: str, content: Any) -> int:
        """
        Broadcast a message to all connected agents
        
        Args:
            message_type (str): Type of message
            content (Any): Message content
            
        Returns:
            int: Number of agents that received the message
        """
        count = 0
        for agent in self.connected_agents:
            if agent.receive_message(self.agent_id, message_type, content):
                count += 1
        
        logger.debug(f"Agent {self.agent_id} broadcast {message_type} message to {count} agents")
        return count
    
    def process(self, input_data: Any) -> Any:
        """
        Process input data
        
        Args:
            input_data (Any): Input data to process
            
        Returns:
            Any: Processed data
        """
        # Base implementation does nothing
        logger.debug(f"Agent {self.agent_id} processing data")
        return input_data
    
    def update_state(self, key: str, value: Any):
        """
        Update agent state
        
        Args:
            key (str): State key
            value (Any): State value
        """
        self.state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get agent state value
        
        Args:
            key (str): State key
            default (Any, optional): Default value if key not found
            
        Returns:
            Any: State value
        """
        return self.state.get(key, default)
    
    def get_full_state(self) -> Dict[str, Any]:
        """
        Get full agent state
        
        Returns:
            Dict[str, Any]: Agent state
        """
        return self.state.copy()