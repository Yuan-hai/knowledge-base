export interface DocumentInfo {
  id: string
  filename: string
  created_at: string
  chunk_count: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  model: string
}

export interface RagQueryRequest {
  query: string
  document_ids: string[]
  model: string
  top_k: number
}

export interface ModelInfo {
  id: string
  name: string
}

export interface SettingsResponse {
  selected_model: string
  upload_folder: string
  available_models: ModelInfo[]
  api_key: string
  api_base_url: string
  api_embedding_url: string
  embedding_model: string
}
