<template>
  <div ref="editorRef" class="h-full w-full overflow-auto" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import {
  EditorView,
  keymap,
  placeholder as placeholderExt,
} from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { defaultKeymap, indentWithTab } from '@codemirror/commands'
import { barf } from 'thememirror'
import { basicSetup } from 'codemirror'

const props = defineProps<{
  modelValue?: string
  readonly?: boolean
  placeholder?: string
  fontSize?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'cursor-change': [line: number, column: number]
}>()

const editorRef = ref<HTMLElement>()
let view: EditorView | null = null

onMounted(() => {
  if (!editorRef.value) return

  const extensions = [
    basicSetup,
    python(),
    barf,
    EditorView.theme({
      '&': { height: '100%', fontSize: props.fontSize || '14px' },
      '.cm-scroller': { overflow: 'auto' },
      '.cm-content': {
        fontFamily: 'JetBrains Mono, Fira Code, Menlo, Monaco, monospace',
      },
      '.cm-gutters': {
        fontFamily: 'JetBrains Mono, Fira Code, Menlo, Monaco, monospace',
      },
    }),
  ]

  if (props.readonly) {
    extensions.push(
      EditorState.readOnly.of(true),
      EditorView.editable.of(false),
    )
  } else {
    extensions.push(
      keymap.of([...defaultKeymap, indentWithTab]),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          emit('update:modelValue', update.state.doc.toString())
        }
        if (update.selectionSet) {
          const pos = update.state.selection.main.head
          const line = update.state.doc.lineAt(pos)
          emit('cursor-change', line.number, pos - line.from)
        }
      }),
    )
  }

  if (props.placeholder) {
    extensions.push(placeholderExt(props.placeholder))
  }

  view = new EditorView({
    state: EditorState.create({
      doc: props.modelValue || '',
      extensions,
    }),
    parent: editorRef.value,
  })
})

onUnmounted(() => {
  view?.destroy()
})

// Update content from outside (e.g., realtime draft updates for spectator)
watch(
  () => props.modelValue,
  (newVal) => {
    if (!view || newVal === undefined) return
    const currentDoc = view.state.doc.toString()
    if (newVal !== currentDoc) {
      view.dispatch({
        changes: { from: 0, to: currentDoc.length, insert: newVal },
      })
    }
  },
)
</script>
