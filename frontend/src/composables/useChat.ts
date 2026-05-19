import { ref, reactive, nextTick, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatMessage } from '../types'

export function useChat() {
  const { t } = useI18n()
  const messages = ref<ChatMessage[]>([])
  const streaming = ref(false)
  const currentModel = ref<string>('')
  const messageSources = reactive<Record<number, string[]>>({})
  let abortController: AbortController | null = null

  onBeforeUnmount(() => {
    abortController?.abort()
  })

  function addMessage(role: 'user' | 'assistant', content: string) {
    messages.value.push({ role, content })
  }

  function clearMessages() {
    messages.value = []
  }

  async function sendChatMessage(content: string, model: string) {
    abortController?.abort()
    abortController = new AbortController()

    addMessage('user', content)
    const assistantMessage: ChatMessage = { role: 'assistant', content: '' }
    messages.value.push(assistantMessage)
    const assistantIndex = messages.value.length - 1

    streaming.value = true
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: messages.value.slice(0, -1),
          model,
        }),
        signal: abortController.signal,
      })

      if (!response.ok) {
        throw new Error(`${t('messages.serverError')} ${response.status}`)
      }

      if (!response.body) {
        throw new Error(t('messages.noResponseBody'))
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
              if (parsed.error) {
                messages.value[assistantIndex].content = `${t('messages.error')} ${parsed.error}`
                break
              }
              const delta =
                parsed.choices?.[0]?.delta?.content ||
                parsed.content ||
                parsed.delta ||
                ''
              messages.value[assistantIndex].content += delta
              await nextTick()
            } catch {
              // Plain text chunk (non-JSON SSE)
              messages.value[assistantIndex].content += data
              await nextTick()
            }
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        messages.value[assistantIndex].content = `${t('messages.error')} ${e.message}`
      }
    } finally {
      streaming.value = false
    }
  }

  async function sendRagQuery(
    query: string,
    documentIds: string[],
    model: string,
    topK: number = 5
  ) {
    abortController?.abort()
    abortController = new AbortController()

    addMessage('user', `[RAG] ${query}`)
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: '',
    }
    messages.value.push(assistantMessage)
    const assistantIndex = messages.value.length - 1
    let sources: string[] = []

    streaming.value = true
    try {
      const response = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          document_ids: documentIds,
          model,
          top_k: topK,
        }),
        signal: abortController.signal,
      })

      if (!response.ok) {
        throw new Error(`${t('messages.serverError')} ${response.status}`)
      }

      if (!response.body) {
        throw new Error(t('messages.noResponseBody'))
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
              if (parsed.error) {
                messages.value[assistantIndex].content = `${t('messages.error')} ${parsed.error}`
                break
              }
              let delta =
                parsed.choices?.[0]?.delta?.content ||
                parsed.content ||
                parsed.delta ||
                ''
              // Check for embedded sources marker in content
              const sourcesMatch = delta.match(/<!--SOURCES:(.*?)-->/)
              if (sourcesMatch) {
                try {
                  const parsedSources = JSON.parse(sourcesMatch[1])
                  sources = parsedSources.data || parsedSources
                } catch { /* ignore */ }
                delta = delta.replace(/<!--SOURCES:.*?-->/, '').trim()
              }
              if (delta) {
                messages.value[assistantIndex].content += delta
                await nextTick()
              }
            } catch {
              messages.value[assistantIndex].content += data
              await nextTick()
            }
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        messages.value[assistantIndex].content = `${t('messages.error')} ${e.message}`
      }
    } finally {
      streaming.value = false
    }

    if (sources.length > 0) {
      messageSources[assistantIndex] = sources
    }
    return sources
  }

  return {
    messages,
    streaming,
    currentModel,
    messageSources,
    addMessage,
    clearMessages,
    sendChatMessage,
    sendRagQuery,
  }
}
