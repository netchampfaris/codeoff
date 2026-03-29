<template>
  <div class="mx-auto max-w-3xl px-6 py-8">
    <div class="mb-6">
      <router-link
        :to="{ name: 'Home' }"
        class="text-ink-gray-5 hover:text-ink-gray-8 inline-flex items-center gap-1 text-sm transition"
      >
        <LucideArrowLeft class="h-4 w-4" />
        Back to ToDos
      </router-link>
    </div>

    <div v-if="todo.doc" class="space-y-6">
      <div class="flex items-start justify-between">
        <h1 class="text-ink-gray-9 text-2xl font-semibold">
          {{ todo.doc.description || 'Untitled ToDo' }}
        </h1>
        <div class="flex items-center gap-2">
          <Badge
            :variant="'subtle'"
            :theme="todo.doc.status === 'Closed' ? 'green' : 'orange'"
            size="md"
          >
            {{ todo.doc.status }}
          </Badge>
          <Button
            variant="ghost"
            theme="red"
            class="rounded-none"
            @click="onDelete"
          >
            <LucideTrash2 class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div class="bg-surface-white rounded-lg border p-6">
        <div class="space-y-4">
          <FormControl
            label="Description"
            type="textarea"
            :modelValue="todo.doc.description"
            @update:modelValue="
              (val: string) => todo.setValue.submit({ description: val })
            "
          />
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              label="Status"
              type="select"
              :options="['Open', 'Closed', 'Cancelled']"
              :modelValue="todo.doc.status"
              @update:modelValue="
                (val: string) => todo.setValue.submit({ status: val })
              "
            />
            <FormControl
              label="Priority"
              type="select"
              :options="['Low', 'Medium', 'High']"
              :modelValue="todo.doc.priority"
              @update:modelValue="
                (val: string) => todo.setValue.submit({ priority: val })
              "
            />
          </div>
          <FormControl
            label="Due Date"
            type="date"
            :modelValue="todo.doc.date"
            @update:modelValue="
              (val: string) => todo.setValue.submit({ date: val })
            "
          />
        </div>
      </div>

      <div class="text-ink-gray-5 text-xs">
        Last modified: {{ todo.doc.modified }}
      </div>
    </div>

    <div
      v-else-if="todo.loading"
      class="flex items-center justify-center py-12"
    >
      <div class="text-ink-gray-5 text-sm">Loading...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useTodo } from '@/data/todos'

const props = defineProps<{
  id: string
}>()

const router = useRouter()
const todo = useTodo(props.id)

async function onDelete() {
  await todo.delete.submit()
  router.push({ name: 'Home' })
}
</script>
