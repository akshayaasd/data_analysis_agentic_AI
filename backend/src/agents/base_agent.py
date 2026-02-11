"""
Base agent class implementing the ReAct (Reasoning + Acting) loop.
All specialized agents inherit from this class.
"""
import re
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from src.services.llm_service import LLMService
from src.tools.python_repl import PythonREPL
from config import settings


class BaseAgent(ABC):
    """
    Base class for all agents using ReAct architecture.
    
    The ReAct loop:
    1. Thought: Agent reasons about what to do
    2. Action: Agent decides on an action
    3. Observation: System provides feedback
    4. Repeat until final answer
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        repl: Optional[PythonREPL] = None,
        max_steps: int = None
    ):
        """
        Initialize base agent.
        
        Args:
            llm_service: LLM service for reasoning
            repl: Python REPL for code execution
            max_steps: Maximum reasoning steps
        """
        self.llm = llm_service
        self.repl = repl or PythonREPL()
        self.max_steps = max_steps or settings.max_agent_steps
        self.steps: List[Dict[str, Any]] = []
        self.plots: List[str] = []
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """
        Get the agent type identifier.
        Must be implemented by subclasses.
        """
        pass
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response to extract thought, action, and final answer.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Dict with 'thought', 'action', 'action_input', 'final_answer'
        """
        parsed = {
            'thought': None,
            'action': None,
            'action_input': None,
            'final_answer': None
        }
        
        # Extract thought
        thought_match = re.search(r'Thought:\s*(.+?)(?=\n(?:Action:|Final Answer:)|$)', response, re.DOTALL)
        if thought_match:
            parsed['thought'] = thought_match.group(1).strip()
        
        # Extract final answer
        final_match = re.search(r'Final Answer:\s*(.+)', response, re.DOTALL)
        if final_match:
            parsed['final_answer'] = final_match.group(1).strip()
            return parsed
        
        # Extract action
        action_match = re.search(r'Action:\s*(.+?)(?=\n|$)', response)
        if action_match:
            parsed['action'] = action_match.group(1).strip()
        
        # Extract action input (code block)
        code_match = re.search(r'```python\n(.+?)\n```', response, re.DOTALL)
        if code_match:
            parsed['action_input'] = code_match.group(1).strip()
        
        return parsed
    
    def execute_action(self, action: str, action_input: str) -> str:
        """
        Execute an action and return observation.
        
        Args:
            action: Action name
            action_input: Action input (usually Python code)
            
        Returns:
            Observation string
        """
        if action.lower() in ['python', 'execute', 'code']:
            result = self.repl.execute(action_input)
            
            if result['success']:
                observation = result['output'] or "Code executed successfully."
                if result['plots']:
                    self.plots.extend(result['plots'])
                    observation += f"\nPlots created: {', '.join(result['plots'])}"
                return observation
            else:
                return f"Error: {result['error']}"
        else:
            return f"Unknown action: {action}"
    
    def build_prompt(self, query: str, history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Build the prompt for the LLM including system prompt and history.
        
        Args:
            query: User query
            history: List of previous steps
            
        Returns:
            List of message dicts
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]
        
        # Add conversation history
        if history:
            history_text = ""
            for step in history:
                if step.get('thought'):
                    history_text += f"\nThought: {step['thought']}"
                if step.get('action'):
                    history_text += f"\nAction: {step['action']}"
                if step.get('action_input'):
                    history_text += f"\n```python\n{step['action_input']}\n```"
                if step.get('observation'):
                    history_text += f"\nObservation: {step['observation']}"
            
            messages.append({"role": "assistant", "content": history_text})
        
        # Add current query
        if not history:
            messages.append({"role": "user", "content": f"Query: {query}"})
        else:
            messages.append({"role": "user", "content": "Continue reasoning or provide final answer."})
        
        return messages
    
    async def run(self, query: str) -> Dict[str, Any]:
        """
        Run the ReAct loop to answer a query.
        
        Args:
            query: User query
            
        Returns:
            Dict with 'final_answer', 'steps', 'total_steps', 'execution_time', 'plots'
        """
        start_time = time.time()
        self.steps = []
        self.plots = []
        
        for step_num in range(1, self.max_steps + 1):
            # Build prompt with history
            messages = self.build_prompt(query, self.steps)
            
            # Get LLM response
            response = await self.llm.generate(messages)
            
            # Parse response
            parsed = self.parse_response(response)
            
            # Create step record
            step = {
                'step_number': step_num,
                'thought': parsed['thought'],
                'action': parsed['action'],
                'action_input': parsed['action_input'],
                'observation': None
            }
            
            # Check if we have a final answer
            if parsed['final_answer']:
                step['final_answer'] = parsed['final_answer']
                self.steps.append(step)
                
                return {
                    'final_answer': parsed['final_answer'],
                    'steps': self.steps,
                    'total_steps': step_num,
                    'execution_time': time.time() - start_time,
                    'plots': self.plots,
                    'agent_type': self.get_agent_type()
                }
            
            # Execute action if present
            if parsed['action'] and parsed['action_input']:
                observation = self.execute_action(parsed['action'], parsed['action_input'])
                step['observation'] = observation
            
            self.steps.append(step)
        
        # Max steps reached - force conclusion
        messages = self.build_prompt(query, self.steps)
        messages.append({
            "role": "user",
            "content": "You've reached the maximum number of steps. Please provide your Final Answer now based on what you've learned."
        })
        
        response = await self.llm.generate(messages)
        parsed = self.parse_response(response)
        
        final_answer = parsed.get('final_answer') or "I was unable to complete the analysis within the step limit."
        
        return {
            'final_answer': final_answer,
            'steps': self.steps,
            'total_steps': self.max_steps,
            'execution_time': time.time() - start_time,
            'plots': self.plots,
            'agent_type': self.get_agent_type()
        }
