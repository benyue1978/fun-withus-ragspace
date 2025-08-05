# RAGSpace UI Design

## Design Principles

### User Experience Goals
- **Simplicity**: Clean, intuitive interface that doesn't overwhelm users
- **Efficiency**: Quick access to common tasks and features
- **Clarity**: Clear visual hierarchy and information organization
- **Responsiveness**: Fast loading and smooth interactions
- **Accessibility**: Support for different user needs and devices

### Design System
- **Color Palette**: Professional, accessible color scheme
- **Typography**: Clear, readable fonts with proper hierarchy
- **Spacing**: Consistent spacing and layout patterns
- **Components**: Reusable UI components for consistency
- **Icons**: Simple, recognizable icons for navigation and actions

## Main Interface Layout

### Navigation Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Logo, Navigation, User Menu                        │
├─────────────────────────────────────────────────────────────┤
│ Sidebar: Knowledge Bases, Recent, Settings                 │
├─────────────────────────────────────────────────────────────┤
│ Main Content Area                                          │
│ ┌─────────────────┐ ┌─────────────────┐                   │
│ │ Upload Panel    │ │ Chat Interface  │                   │
│ │                 │ │                 │                   │
│ │ • File Upload   │ │ • Message List  │                   │
│ │ • URL Input     │ │ • Input Field   │                   │
│ │ • GitHub Repo   │ │ • Send Button   │                   │
│ └─────────────────┘ └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## Component Designs

### 1. Header Component
```html
<!-- Header with navigation and user menu -->
<header class="header">
  <div class="header-left">
    <div class="logo">
      <img src="/logo.svg" alt="RAGSpace" />
      <span class="logo-text">RAGSpace</span>
    </div>
    <nav class="main-nav">
      <a href="/dashboard" class="nav-item">Dashboard</a>
      <a href="/knowledge-bases" class="nav-item">Knowledge Bases</a>
      <a href="/chat" class="nav-item">Chat</a>
      <a href="/settings" class="nav-item">Settings</a>
    </nav>
  </div>
  <div class="header-right">
    <div class="user-menu">
      <button class="user-avatar">
        <img src="/avatar.jpg" alt="User" />
      </button>
      <div class="user-dropdown">
        <a href="/profile">Profile</a>
        <a href="/api-keys">API Keys</a>
        <a href="/logout">Logout</a>
      </div>
    </div>
  </div>
</header>
```

**CSS Styling**:
```css
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1.25rem;
  color: #1f2937;
}

.main-nav {
  display: flex;
  gap: 2rem;
  margin-left: 2rem;
}

.nav-item {
  color: #6b7280;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.nav-item:hover {
  color: #1f2937;
  background: #f3f4f6;
}

.nav-item.active {
  color: #3b82f6;
  background: #eff6ff;
}
```

### 2. Sidebar Component
```html
<!-- Sidebar with knowledge bases and quick actions -->
<aside class="sidebar">
  <div class="sidebar-section">
    <h3 class="section-title">Knowledge Bases</h3>
    <div class="kb-list">
      <div class="kb-item active">
        <div class="kb-icon">📚</div>
        <div class="kb-info">
          <div class="kb-name">Python Documentation</div>
          <div class="kb-stats">1.2k documents</div>
        </div>
      </div>
      <div class="kb-item">
        <div class="kb-icon">🔧</div>
        <div class="kb-info">
          <div class="kb-name">API Reference</div>
          <div class="kb-stats">856 documents</div>
        </div>
      </div>
    </div>
    <button class="add-kb-btn">+ New Knowledge Base</button>
  </div>
  
  <div class="sidebar-section">
    <h3 class="section-title">Recent Queries</h3>
    <div class="recent-queries">
      <div class="query-item">How to use async/await?</div>
      <div class="query-item">What is dependency injection?</div>
      <div class="query-item">Explain the observer pattern</div>
    </div>
  </div>
</aside>
```

**CSS Styling**:
```css
.sidebar {
  width: 280px;
  background: #f9fafb;
  border-right: 1px solid #e5e7eb;
  padding: 1.5rem;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kb-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-item:hover {
  background: #f3f4f6;
}

.kb-item.active {
  background: #eff6ff;
  border: 1px solid #3b82f6;
}

.kb-icon {
  font-size: 1.25rem;
}

.kb-name {
  font-weight: 500;
  color: #1f2937;
}

.kb-stats {
  font-size: 0.75rem;
  color: #6b7280;
}

.add-kb-btn {
  width: 100%;
  padding: 0.75rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.add-kb-btn:hover {
  background: #2563eb;
}
```

### 3. Upload Panel Component
```html
<!-- Upload panel for adding new content -->
<div class="upload-panel">
  <h3 class="panel-title">Add Content</h3>
  
  <div class="upload-tabs">
    <button class="tab-btn active" data-tab="file">File Upload</button>
    <button class="tab-btn" data-tab="url">URL</button>
    <button class="tab-btn" data-tab="github">GitHub</button>
  </div>
  
  <div class="tab-content active" id="file-tab">
    <div class="upload-area">
      <div class="upload-icon">📁</div>
      <p class="upload-text">Drag and drop files here or click to browse</p>
      <input type="file" multiple class="file-input" />
      <button class="browse-btn">Browse Files</button>
    </div>
    <div class="supported-formats">
      Supported: PDF, TXT, MD, DOCX, HTML
    </div>
  </div>
  
  <div class="tab-content" id="url-tab">
    <div class="input-group">
      <label for="url-input">Website URL</label>
      <input type="url" id="url-input" placeholder="https://example.com/docs" />
      <button class="fetch-btn">Fetch Content</button>
    </div>
  </div>
  
  <div class="tab-content" id="github-tab">
    <div class="input-group">
      <label for="github-repo">GitHub Repository</label>
      <input type="text" id="github-repo" placeholder="owner/repository" />
      <button class="fetch-btn">Import Repository</button>
    </div>
    <div class="github-options">
      <label class="checkbox">
        <input type="checkbox" checked />
        Include README and documentation
      </label>
      <label class="checkbox">
        <input type="checkbox" checked />
        Include source code files
      </label>
    </div>
  </div>
</div>
```

**CSS Styling**:
```css
.upload-panel {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.panel-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.upload-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  background: none;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  transition: border-color 0.2s;
}

.upload-area:hover {
  border-color: #3b82f6;
}

.upload-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.upload-text {
  color: #6b7280;
  margin-bottom: 1rem;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.input-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.fetch-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 0.5rem;
}
```

### 4. Chat Interface Component
```html
<!-- Chat interface for querying knowledge base -->
<div class="chat-interface">
  <div class="chat-header">
    <h3 class="chat-title">Chat with Knowledge Base</h3>
    <div class="chat-actions">
      <button class="action-btn" title="Clear Chat">🗑️</button>
      <button class="action-btn" title="Export Chat">📤</button>
    </div>
  </div>
  
  <div class="chat-messages">
    <div class="message user-message">
      <div class="message-avatar">👤</div>
      <div class="message-content">
        <div class="message-text">How do I implement authentication in FastAPI?</div>
        <div class="message-time">2:30 PM</div>
      </div>
    </div>
    
    <div class="message assistant-message">
      <div class="message-avatar">🤖</div>
      <div class="message-content">
        <div class="message-text">
          To implement authentication in FastAPI, you can use several approaches:
          
          1. **JWT Tokens**: Use `python-jose` for JWT handling
          2. **OAuth2**: Built-in support with `python-multipart`
          3. **Session-based**: Use `fastapi-session`
          
          Here's a basic JWT example:
          ```python
          from fastapi import Depends, HTTPException
          from fastapi.security import HTTPBearer
          
          security = HTTPBearer()
          
          async def get_current_user(token: str = Depends(security)):
              # Verify token and return user
              pass
          ```
        </div>
        <div class="message-sources">
          <div class="source-item">📄 FastAPI Security Documentation</div>
          <div class="source-item">📄 Authentication Best Practices</div>
        </div>
        <div class="message-time">2:31 PM</div>
      </div>
    </div>
  </div>
  
  <div class="chat-input">
    <div class="input-container">
      <textarea 
        class="message-input" 
        placeholder="Ask a question about your knowledge base..."
        rows="3"
      ></textarea>
      <button class="send-btn" disabled>Send</button>
    </div>
    <div class="input-actions">
      <button class="action-btn" title="Upload File">📎</button>
      <button class="action-btn" title="Voice Input">🎤</button>
    </div>
  </div>
</div>
```

**CSS Styling**:
```css
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.chat-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
}

.message {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.message-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.user-message .message-avatar {
  background: #3b82f6;
  color: white;
}

.assistant-message .message-avatar {
  background: #10b981;
  color: white;
}

.message-content {
  flex: 1;
}

.message-text {
  background: #f9fafb;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  line-height: 1.5;
  white-space: pre-wrap;
}

.user-message .message-text {
  background: #eff6ff;
  color: #1e40af;
}

.message-sources {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.source-item {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.message-time {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.chat-input {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.input-container {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  resize: none;
  font-family: inherit;
  font-size: 0.875rem;
}

.message-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.send-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #2563eb;
}

.send-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.input-actions {
  display: flex;
  gap: 0.5rem;
}
```

## Responsive Design

### Mobile Layout
```css
/* Mobile responsive styles */
@media (max-width: 768px) {
  .header {
    padding: 0.75rem 1rem;
  }
  
  .main-nav {
    display: none; /* Hide on mobile, use hamburger menu */
  }
  
  .sidebar {
    position: fixed;
    left: -280px;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s;
  }
  
  .sidebar.open {
    left: 0;
  }
  
  .upload-panel,
  .chat-interface {
    margin: 1rem;
  }
  
  .chat-messages {
    padding: 0.75rem 1rem;
  }
  
  .message {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .message-avatar {
    align-self: flex-start;
  }
}
```

### Tablet Layout
```css
/* Tablet responsive styles */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }
  
  .upload-panel,
  .chat-interface {
    margin: 1rem;
  }
}
```

## Accessibility Features

### Keyboard Navigation
```css
/* Focus styles for keyboard navigation */
.nav-item:focus,
.tab-btn:focus,
.action-btn:focus,
.send-btn:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Skip to main content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: #3b82f6;
  color: white;
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1001;
}

.skip-link:focus {
  top: 6px;
}
```

### Screen Reader Support
```html
<!-- ARIA labels and roles -->
<button class="action-btn" aria-label="Clear chat history">
  🗑️
</button>

<div class="chat-messages" role="log" aria-live="polite">
  <!-- Messages -->
</div>

<div class="message-sources" role="complementary" aria-label="Sources">
  <!-- Source items -->
</div>
```

## Loading States

### Loading Indicators
```css
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## Error States

### Error Handling UI
```css
.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.error-message .error-icon {
  margin-right: 0.5rem;
}

.warning-message {
  background: #fffbeb;
  border: 1px solid #fed7aa;
  color: #d97706;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}
```

## Dark Mode Support

### Dark Theme Variables
```css
:root {
  /* Light theme */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --accent-color: #3b82f6;
}

[data-theme="dark"] {
  /* Dark theme */
  --bg-primary: #1f2937;
  --bg-secondary: #111827;
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --border-color: #374151;
  --accent-color: #60a5fa;
}
```

This comprehensive UI design provides a clean, modern interface that prioritizes usability and accessibility while maintaining visual appeal and professional appearance.