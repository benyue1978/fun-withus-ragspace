"""
Base Component for Gradio UI Components
Provides unified state management and event handling
"""

import gradio as gr
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class ComponentState:
    """Base state class for components"""
    initialized: bool = False
    data: Dict[str, Any] = field(default_factory=dict)


class BaseComponent:
    """Base class for all Gradio components"""
    
    def __init__(self, name: str):
        self.name = name
        self.state = gr.State(ComponentState())
        self.components: Dict[str, gr.Component] = {}
        self.event_handlers: List[Callable] = []
    
    def create_ui(self) -> gr.Component:
        """Create the UI components - to be implemented by subclasses"""
        raise NotImplementedError
    
    def setup_events(self):
        """Setup event handlers - to be implemented by subclasses"""
        pass
    
    def get_component(self, name: str) -> Optional[gr.Component]:
        """Get a component by name"""
        return self.components.get(name)
    
    def add_component(self, name: str, component: gr.Component):
        """Add a component to the component registry"""
        self.components[name] = component
    
    def add_event_handler(self, handler: Callable):
        """Add an event handler"""
        self.event_handlers.append(handler)
    
    def update_state(self, **kwargs):
        """Update component state"""
        return gr.State(ComponentState(
            initialized=True,
            data={**kwargs}
        ))
    
    def get_state_data(self, state: ComponentState, key: str, default: Any = None):
        """Get data from state"""
        return state.data.get(key, default)
