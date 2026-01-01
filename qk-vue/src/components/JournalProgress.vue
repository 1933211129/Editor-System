<template>
  <div class="main-content">
    <h3>📌期刊文章进度管理</h3>
    <div class="period-nav mb-4">
      <div class="btn-group">
        <div v-for="(period, index) in periods" :key="index" class="period-item">
          <button 
            class="btn period-btn"
            :class="[currentPeriod === index ? 'btn-primary' : 'btn-outline-primary']"
            @click="currentPeriod = index"
          >
            第{{ period.number }}期
            <select 
              v-model="period.number" 
              class="period-number-select"
              @click.stop
              @change="savePeriodNumbers"
            >
              <option v-for="n in 12" :key="n" :value="n">第{{ n }}期</option>
            </select>
          </button>
        </div>
      </div>
    </div>

    <!-- 动态组件切换不同期数 -->
    <component 
      :is="periods[currentPeriod].component" 
      :displayPeriod="periods[currentPeriod].number"
      :backendPeriod="periods[currentPeriod].backendPeriod"
    ></component>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import JournalPeriodOne from './journal/JournalPeriodOne.vue';
import JournalPeriodTwo from './journal/JournalPeriodTwo.vue';
import JournalPeriodThree from './journal/JournalPeriodThree.vue';
import JournalPeriodFour from './journal/JournalPeriodFour.vue';
import JournalPeriodFive from './journal/JournalPeriodFive.vue';

const currentPeriod = ref(0);
const saveStatus = ref('');

const components = [
  JournalPeriodOne,
  JournalPeriodTwo,
  JournalPeriodThree,
  JournalPeriodFour,
  JournalPeriodFive
];

const periods = ref(components.map((component, index) => ({
  number: index + 1, // 初始显示值
  backendPeriod: index + 1, // 固定的后端期数，用于 API 调用
  component
})));

// 在组件挂载时加载映射
onMounted(async () => {
  try {
    const response = await axios.get('/api/journal/period-mapping/')
    const mappings = response.data
    
    // 只更新显示期数，保持后端期数不变
    periods.value = components.map((component, index) => ({
      number: mappings[index + 1] || index + 1, // 显示期数
      backendPeriod: index + 1, // 固定的后端期数
      component
    }))
  } catch (error) {
    console.error('加载期数映射失败:', error)
  }
})

const savePeriodNumbers = async () => {
  periods.value.forEach((period) => {
    updatePeriodMapping(period.backendPeriod, period.number);
  });
};

const updatePeriodMapping = async (backendPeriod, displayPeriod) => {
  try {
    saveStatus.value = '保存中...';
    
    const response = await axios.post('/api/journal/period-mapping/update/', {
      backend_period: backendPeriod,
      display_period: displayPeriod
    });
    
    if (response.data.status === 'success') {
      saveStatus.value = '已保存';
    } else {
      throw new Error(response.data.message || '更新失败');
    }
  } catch (error) {
    console.error('更新期数失败:', error);
    saveStatus.value = '保存失败';
  }
};
</script>

<style scoped>
.period-nav {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.main-content {
  margin-left: 250px;
  padding: 20px;
}

.period-item {
  position: relative;
  display: inline-block;
  margin: 0 2px;
}

.period-btn {
  min-width: 80px;
  position: relative;
  padding-right: 30px;
}

.period-number-select {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 30px;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
  background-color: white;
}

.period-number-select option {
  color: #333;
  background-color: white;
  padding: 8px;
}

.period-btn::after {
  content: "▼";
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  pointer-events: none;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
}
</style> 
