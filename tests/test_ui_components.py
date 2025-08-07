"""
Tests for UI Components with improved architecture
Testing component initialization, state management, and UI updates
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import gradio as gr
from src.ragspace.ui.components.base_component import BaseComponent, ComponentState
from src.ragspace.ui.components.knowledge_management import KnowledgeManagementComponent
from src.ragspace.ui.components.chat_interface import ChatInterfaceComponent
from src.ragspace.ui.components.mcp_tools import MCPToolsComponent


class TestBaseComponent:
    """Test the base component functionality"""
    
    def test_base_component_initialization(self):
        """Test base component initialization"""
        component = BaseComponent("test_component")
        
        assert component.name == "test_component"
        assert isinstance(component.state, gr.State)
        assert isinstance(component.components, dict)
        assert isinstance(component.event_handlers, list)
    
    def test_component_registration(self):
        """Test component registration system"""
        component = BaseComponent("test_component")
        
        # Mock gradio component
        mock_component = Mock()
        mock_component.name = "test_button"
        
        # Register component
        component.add_component("test_button", mock_component)
        
        # Retrieve component
        retrieved = component.get_component("test_button")
        assert retrieved == mock_component
        
        # Test non-existent component
        non_existent = component.get_component("non_existent")
        assert non_existent is None
    
    def test_state_management(self):
        """Test state management functionality"""
        component = BaseComponent("test_component")
        
        # Test initial state
        initial_state = component.state.value
        assert isinstance(initial_state, ComponentState)
        assert initial_state.initialized == False
        assert initial_state.data == {}
        
        # Test state update
        updated_state = component.update_state(key1="value1", key2="value2")
        assert updated_state.value.data["key1"] == "value1"
        assert updated_state.value.data["key2"] == "value2"
        assert updated_state.value.initialized == True
    
    def test_get_state_data(self):
        """Test getting data from state"""
        component = BaseComponent("test_component")
        
        # Test with default value
        data = component.get_state_data(ComponentState(), "non_existent", "default")
        assert data == "default"
        
        # Test with existing data
        state = ComponentState(data={"key": "value"})
        data = component.get_state_data(state, "key", "default")
        assert data == "value"


class TestKnowledgeManagementComponent:
    """Test the Knowledge Management component"""
    
    @pytest.fixture
    def mock_docset_manager(self):
        """Mock docset manager"""
        mock_manager = Mock()
        mock_manager.get_docsets_dict.return_value = {
            "test-docset-1": {"name": "test-docset-1", "description": "Test 1"},
            "test-docset-2": {"name": "test-docset-2", "description": "Test 2"}
        }
        return mock_manager
    
    def test_component_initialization(self, mock_docset_manager):
        """Test component initialization"""
        with patch('src.ragspace.ui.components.knowledge_management.KnowledgeManagementComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = KnowledgeManagementComponent()
            
            assert component.name == "knowledge_management"
            assert component.docset_manager == mock_docset_manager
    
    def test_get_initial_data_success(self, mock_docset_manager):
        """Test getting initial data successfully"""
        with patch('src.ragspace.ui.components.knowledge_management.KnowledgeManagementComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = KnowledgeManagementComponent()
            initial_data = component._get_initial_data()
            
            assert initial_data["choices"] == ["test-docset-1", "test-docset-2"]
            assert initial_data["selected"] == "test-docset-1"
            assert "initial_info" in initial_data
            assert "initial_documents" in initial_data
    
    def test_get_initial_data_empty(self, mock_docset_manager):
        """Test getting initial data when no docsets exist"""
        mock_docset_manager.get_docsets_dict.return_value = {}
        
        with patch('src.ragspace.ui.components.knowledge_management.KnowledgeManagementComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = KnowledgeManagementComponent()
            initial_data = component._get_initial_data()
            
            assert initial_data["choices"] == []
            assert initial_data["selected"] is None
            assert initial_data["initial_info"] == ""
            assert initial_data["initial_documents"] == []
    
    def test_get_initial_data_error(self, mock_docset_manager):
        """Test getting initial data when error occurs"""
        mock_docset_manager.get_docsets_dict.side_effect = Exception("Database error")
        
        with patch('src.ragspace.ui.components.knowledge_management.KnowledgeManagementComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = KnowledgeManagementComponent()
            initial_data = component._get_initial_data()
            
            assert initial_data["choices"] == []
            assert initial_data["selected"] is None
            assert initial_data["initial_info"] == ""
            assert initial_data["initial_documents"] == []
    
    def test_get_docset_info(self):
        """Test getting docset info"""
        component = KnowledgeManagementComponent()
        
        # Test with None docset_name
        info = component._get_docset_info(None)
        assert info == ""
        
        # Test with valid docset_name
        with patch('src.ragspace.ui.handlers.get_docset_data') as mock_get_data:
            mock_get_data.return_value = (
                {"name": "test", "description": "Test docset"},
                [{"name": "doc1", "type": "file"}],
                None
            )
            
            with patch('src.ragspace.ui.handlers.create_docset_info_text') as mock_create_text:
                mock_create_text.return_value = "Test info text"
                
                info = component._get_docset_info("test-docset")
                assert info == "Test info text"
    
    def test_get_documents_data(self):
        """Test getting documents data"""
        component = KnowledgeManagementComponent()
        
        # Test with None docset_name
        data = component._get_documents_data(None)
        assert data == []
        
        # Test with valid docset_name
        with patch('src.ragspace.ui.handlers.get_docset_data') as mock_get_data:
            mock_get_data.return_value = (
                {"name": "test", "description": "Test docset"},
                [{"name": "doc1", "type": "file"}],
                None
            )
            
            with patch('src.ragspace.ui.handlers.convert_documents_to_dataframe') as mock_convert:
                mock_convert.return_value = [["doc1", "file", "N/A", "Unknown", "pending"]]
                
                data = component._get_documents_data("test-docset")
                assert data == [["doc1", "file", "N/A", "Unknown", "pending"]]


class TestChatInterfaceComponent:
    """Test the Chat Interface component"""
    
    @pytest.fixture
    def mock_docset_manager(self):
        """Mock docset manager"""
        mock_manager = Mock()
        mock_manager.get_docsets_dict.return_value = {
            "test-docset-1": {"name": "test-docset-1", "description": "Test 1"},
            "test-docset-2": {"name": "test-docset-2", "description": "Test 2"}
        }
        return mock_manager
    
    def test_component_initialization(self, mock_docset_manager):
        """Test component initialization"""
        with patch('src.ragspace.ui.components.chat_interface.ChatInterfaceComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = ChatInterfaceComponent()
            
            assert component.name == "chat_interface"
            assert component.docset_manager == mock_docset_manager
    
    def test_get_initial_data_success(self, mock_docset_manager):
        """Test getting initial data successfully"""
        with patch('src.ragspace.ui.components.chat_interface.ChatInterfaceComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = ChatInterfaceComponent()
            initial_data = component._get_initial_data()
            
            assert initial_data["choices"] == ["test-docset-1", "test-docset-2"]
            assert initial_data["selected"] == "test-docset-1"
    
    def test_get_initial_data_empty(self, mock_docset_manager):
        """Test getting initial data when no docsets exist"""
        mock_docset_manager.get_docsets_dict.return_value = {}
        
        with patch('src.ragspace.ui.components.chat_interface.ChatInterfaceComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = ChatInterfaceComponent()
            initial_data = component._get_initial_data()
            
            assert initial_data["choices"] == []
            assert initial_data["selected"] is None


class TestMCPToolsComponent:
    """Test the MCP Tools component"""
    
    @pytest.fixture
    def mock_docset_manager(self):
        """Mock docset manager"""
        mock_manager = Mock()
        mock_manager.get_docsets_dict.return_value = {
            "test-docset-1": {"name": "test-docset-1", "description": "Test 1"},
            "test-docset-2": {"name": "test-docset-2", "description": "Test 2"}
        }
        return mock_manager
    
    def test_component_initialization(self, mock_docset_manager):
        """Test component initialization"""
        with patch('src.ragspace.ui.components.mcp_tools.MCPToolsComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = MCPToolsComponent()
            
            assert component.name == "mcp_tools"
            assert component.docset_manager == mock_docset_manager
    
    def test_get_initial_data_success(self, mock_docset_manager):
        """Test getting initial data successfully"""
        with patch('src.ragspace.ui.components.mcp_tools.MCPToolsComponent._get_docset_manager') as mock_get_manager:
            mock_get_manager.return_value = mock_docset_manager
            
            component = MCPToolsComponent()
            initial_data = component._get_initial_data()
            
            assert initial_data["choices"] == ["test-docset-1", "test-docset-2"]


class TestUIStateManagement:
    """Test UI state management scenarios"""
    
    def test_component_state_persistence(self):
        """Test that component state persists across operations"""
        component = KnowledgeManagementComponent()
        
        # Initial state
        initial_state = component.state.value
        assert initial_state.initialized == False
        
        # Update state
        updated_state = component.update_state(
            selected_docset="test-docset",
            documents_count=5
        )
        
        # Verify state update
        assert updated_state.value.initialized == True
        assert updated_state.value.data["selected_docset"] == "test-docset"
        assert updated_state.value.data["documents_count"] == 5
    
    def test_component_isolation(self):
        """Test that components are isolated from each other"""
        km_component = KnowledgeManagementComponent()
        chat_component = ChatInterfaceComponent()
        
        # Each component should have its own state
        assert km_component.name != chat_component.name
        assert km_component.state != chat_component.state
    
    def test_component_registry_isolation(self):
        """Test that component registries are isolated"""
        km_component = KnowledgeManagementComponent()
        chat_component = ChatInterfaceComponent()
        
        # Add components with same name to different registries
        km_component.add_component("test_button", Mock())
        chat_component.add_component("test_button", Mock())
        
        # Components should be isolated
        assert km_component.get_component("test_button") != chat_component.get_component("test_button")


class TestUIInitialization:
    """Test UI initialization scenarios"""
    
    def test_ui_initialization_with_data(self):
        """Test UI initialization when data is available"""
        with patch('src.ragspace.ui.components.knowledge_management.KnowledgeManagementComponent._get_docset_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_docsets_dict.return_value = {
                "test-docset": {"name": "test-docset", "description": "Test"}
            }
            mock_get_manager.return_value = mock_manager
            
            component = KnowledgeManagementComponent()
            initial_data = component._get_initial_data()
            
            # Verify initialization data
            assert initial_data["choices"] == ["test-docset"]
            assert initial_data["selected"] == "test-docset"
            assert "initial_info" in initial_data
            assert "initial_documents" in initial_data
    
    def test_ui_initialization_without_data(self):
        """Test UI initialization when no data is available"""
        with patch('src.ragspace.ui.components.knowledge_management.KnowledgeManagementComponent._get_docset_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_docsets_dict.return_value = {}
            mock_get_manager.return_value = mock_manager
            
            component = KnowledgeManagementComponent()
            initial_data = component._get_initial_data()
            
            # Verify initialization data
            assert initial_data["choices"] == []
            assert initial_data["selected"] is None
            assert initial_data["initial_info"] == ""
            assert initial_data["initial_documents"] == []
    
    def test_ui_initialization_error_handling(self):
        """Test UI initialization error handling"""
        with patch('src.ragspace.ui.components.knowledge_management.KnowledgeManagementComponent._get_docset_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_docsets_dict.side_effect = Exception("Database error")
            mock_get_manager.return_value = mock_manager
            
            component = KnowledgeManagementComponent()
            initial_data = component._get_initial_data()
            
            # Verify error handling
            assert initial_data["choices"] == []
            assert initial_data["selected"] is None
            assert initial_data["initial_info"] == ""
            assert initial_data["initial_documents"] == []


class TestUIEventChaining:
    """Test UI event chaining scenarios"""
    
    def test_event_chain_completeness(self):
        """Test that event chains are complete"""
        component = KnowledgeManagementComponent()
        
        # Verify that all necessary event handlers are set up
        assert hasattr(component, '_setup_docset_events')
        assert hasattr(component, '_setup_document_events')
        assert hasattr(component, '_setup_upload_events')
    
    def test_event_handler_registration(self):
        """Test that event handlers are properly registered"""
        component = KnowledgeManagementComponent()
        
        # Add a mock event handler
        mock_handler = Mock()
        component.add_event_handler(mock_handler)
        
        # Verify handler is registered
        assert mock_handler in component.event_handlers
    
    def test_component_retrieval_for_events(self):
        """Test that components can be retrieved for event binding"""
        component = KnowledgeManagementComponent()
        
        # Mock a component
        mock_button = Mock()
        component.add_component("test_button", mock_button)
        
        # Retrieve component for event binding
        retrieved_button = component.get_component("test_button")
        assert retrieved_button == mock_button
