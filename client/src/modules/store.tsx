import React from 'react'
import { create } from 'zustand'

type Message = {
  sender: string
  text: string
  imageUrl?: string
}

type Model = {
  name: string
  provider: string
}

type Store = {
  count: number
  messages: Message[]
  input: string
  model: Model
  models: Model[]
  chatState: { isSidebarOpened: boolean }
  inc: () => void
  setMessages: (messages: Message[]) => void
  setInput: (input: string) => void
  setModel: (model: Model) => void
  setModels: (models: Model[]) => void
  toggleSidebar: () => void
}

export const useStore = create<Store>()((set) => ({
  count: 1,
  messages: [],
  input: "",
  model: { name: "gpt-4o", provider: "openai" },
  models: [
    { name: "gpt-4o", provider: "openai" },
    { name: "gpt-4o-mini", provider: "openai" },
  ],
  chatState: { isSidebarOpened: false },
  inc: () => set((state) => ({ count: state.count + 1 })),
  setMessages: (messages) => set({ messages }),
  setInput: (input) => set({ input }),
  setModel: (model) => set({ model }),
  setModels: (models) => set({ models }),
  toggleSidebar: () => set((state) => ({ chatState: { isSidebarOpened: !state.chatState.isSidebarOpened } })),
}))

export function Counter() {
  const { count, inc } = useStore()
  return (
    <div>
      <span>{count}</span>
      <button onClick={inc}>one up</button>
    </div>
  )
}
