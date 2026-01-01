<template>
  <div>
    <!-- 你的模板内容 -->
  </div>
</template>

<script setup>
// 如果使用 Vue 3.3+ 版本，不需要导入 defineProps
// 如果使用较早版本，需要添加下面这行：
// import { defineProps } from 'vue'

const props = defineProps({
  // 定义具体的 props
  title: {
    type: String,
    default: ''
  }
})
</script> 