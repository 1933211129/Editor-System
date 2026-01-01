<template>
  <JournalPeriodBase :displayPeriod="displayPeriod" :backendPeriod="backendPeriod" />
</template>

<script setup>
import { defineProps } from 'vue'
import JournalPeriodBase from './JournalPeriodBase.vue'

defineProps({
  displayPeriod: {
    type: Number,
    required: true
  },
  backendPeriod: {
    type: Number,
    required: true
  }
})
</script> 
