<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  options: { type: Array, default: () => [] },
  groups: { type: Array, default: null }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const wrapperRef = ref(null)

const allItems = computed(() => {
  if (props.groups) {
    return props.groups.flatMap(g => g.items)
  }
  return props.options
})

const selectedLabel = computed(() => {
  const item = allItems.value.find(o => String(o.value) === String(props.modelValue))
  return item ? item.label : ''
})

const select = (value) => {
  emit('update:modelValue', value)
  isOpen.value = false
}

const toggle = () => {
  isOpen.value = !isOpen.value
}

const onClickOutside = (e) => {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="app-select-wrapper" ref="wrapperRef">
    <button class="app-select-trigger" type="button" @click="toggle">
      <span class="app-select-text">{{ selectedLabel }}</span>
      <span class="app-select-arrow">▼</span>
    </button>
    <div v-if="isOpen" class="app-select-dropdown">
      <template v-if="groups">
        <template v-for="g in groups" :key="g.label">
          <div class="app-select-group">{{ g.label }}</div>
          <button
            v-for="item in g.items"
            :key="item.value"
            class="app-select-option"
            :class="{ active: String(item.value) === String(modelValue) }"
            @click="select(item.value)"
          >
            {{ item.label }}
          </button>
        </template>
      </template>
      <template v-else>
        <button
          v-for="opt in options"
          :key="opt.value"
          class="app-select-option"
          :class="{ active: String(opt.value) === String(modelValue) }"
          @click="select(opt.value)"
        >
          {{ opt.label }}
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.app-select-wrapper {
  position: relative;
}

.app-select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  width: 100%;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #1a1a2e;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.app-select-trigger:hover {
  border-color: #4575b4;
}

.app-select-trigger:focus {
  outline: none;
  border-color: #4575b4;
  box-shadow: 0 0 0 2px rgba(69, 117, 180, 0.15);
}

.app-select-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-select-arrow {
  font-size: 0.625rem;
  color: #718096;
  flex-shrink: 0;
}

.app-select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  min-width: 200px;
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
  z-index: 100;
}

.app-select-group {
  padding: 0.375rem 0.75rem;
  font-size: 0.625rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
}

.app-select-option {
  display: block;
  width: 100%;
  padding: 0.4375rem 0.75rem;
  background: none;
  border: none;
  font-size: 0.875rem;
  text-align: left;
  cursor: pointer;
  color: #334155;
  transition: background 0.15s;
}

.app-select-option:hover {
  background: #f1f5f9;
}

.app-select-option.active {
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 500;
}

.app-select-option + .app-select-option {
  border-top: 1px solid #f8fafc;
}

.app-select-group + .app-select-option {
  border-top: none;
}

@media (max-width: 768px) {
  .app-select-wrapper {
    width: 100%;
  }

  .app-select-trigger {
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
  }

  .app-select-option {
    font-size: 0.8rem;
    padding: 0.4rem 0.75rem;
  }
}
</style>
