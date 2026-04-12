"""
Base agent class implementing the ReAct (Reasoning + Acting) loop.
All specialized agents inherit from this class.
"""
import re
import time
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from src.services.llm_service import LLMService
from src.tools.python_repl import PythonREPL
from config import settings

logger = logging.getLogger(__name__)


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
        Parse raw LLM response into thought, action, and action_input.
        """
        parsed = {
            'thought': None,
            'action': None,
            'action_input': None,
            'final_answer': None
        }
        
        # Extract thought
        thought_match = re.search(r'Thought:\s*(.+?)(?=\nAction:|\nFinal Answer:|$)', response, re.DOTALL)
        if thought_match:
            parsed['thought'] = thought_match.group(1).strip()
        else:
            # Fallback for models that skip "Thought:"
            # Look for everything before the first Action or Final Answer
            thought_match = re.search(r'^(.+?)(?=\nAction:|\nFinal Answer:|$)', response, re.DOTALL)
            if thought_match:
                parsed['thought'] = thought_match.group(1).strip()
            elif not any(x in response for x in ["Action:", "Final Answer:"]):
                # If neither is present, the whole thing might be a thought/answer
                parsed['thought'] = response.strip()

        # Extract final answer
        final_answer_match = re.search(r'Final Answer:\s*(.+)', response, re.DOTALL)
        if final_answer_match:
            parsed['final_answer'] = final_answer_match.group(1).strip()
        
        # Extract action - Allow for trailing whitespace and missing action names
        action_match = re.search(r'Action:\s*(.+?)(?=\n|$)', response)
        if action_match:
            parsed['action'] = action_match.group(1).strip()
            
            # Extract action input (code block)
            code_match = re.search(r'```python\n(.+?)\n```', response, re.DOTALL)
            if code_match:
                parsed['action_input'] = code_match.group(1).strip()
            
            # Special case: If action is just ```python, it means the model skipped the name
            if parsed['action'].startswith('```python') or not parsed['action']:
                if parsed['action_input']:
                    parsed['action'] = 'Python'
        
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
                    logger.info(f"Adding plots to agent: {result['plots']}")
                    self.plots.extend(result['plots'])
                    observation += f"\nPlots created: {', '.join(result['plots'])}"
                return observation
            else:
                logger.error(f"Execution error: {result['error']}")
                return f"Error: {result['error']}"
        else:
            logger.warning(f"Unknown action: {action}")
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
        
        # Add conversation history as separate messages
        if history:
            for step in history:
                # Agent turn
                assistant_content = ""
                if step.get('thought'):
                    assistant_content += f"Thought: {step['thought']}"
                if step.get('action'):
                    if assistant_content: assistant_content += "\n"
                    assistant_content += f"Action: {step['action']}"
                if step.get('action_input'):
                    if assistant_content: assistant_content += "\n"
                    assistant_content += f"```python\n{step['action_input']}\n```"
                
                if assistant_content:
                    messages.append({"role": "assistant", "content": assistant_content})
                
                # System observation turn
                if step.get('observation'):
                    messages.append({"role": "user", "content": f"Observation: {step['observation']}"})
        
        # Add current query
        if not history:
            messages.append({"role": "user", "content": f"Query: {query}"})
        else:
            # If the last message was a thought/action, the LLM should have received an observation already
            # If the last message was an observation, we just want it to continue
            if messages[-1]["role"] == "assistant":
                # This should only happen if execution failed or something went wrong
                messages.append({"role": "user", "content": "Please continue with the next step or final answer."})
        
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
            logger.info(f"Step {step_num} raw response: {response}")
            
            # Parse response
            parsed = self.parse_response(response)
            logger.info(f"Step {step_num} parsed: {parsed}")
            
            # Create step record
            step = {
                'step_number': step_num,
                'thought': parsed['thought'],
                'action': parsed['action'],
                'action_input': parsed['action_input'],
                'observation': None
            }
            
            # Execute action if present (Do this BEFORE checking for Final Answer)
            if parsed.get('action') and parsed.get('action_input'):
                observation = self.execute_action(parsed['action'], parsed['action_input'])
                step['observation'] = observation
            
            # Check if we have a final answer
            if parsed.get('final_answer'):
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
            
            # If no action was taken and no final answer was given, the agent might be stuck or just providing a thought
            # We continue the loop and build_prompt will add a "Please continue" message if needed
            
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
