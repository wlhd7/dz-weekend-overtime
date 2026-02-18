<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script lang="ts">
export default {
  name: 'App'
}
</script>

<style>
/* Global styles matching original CSS */
.staff-list {
  display: grid;
  width: 100%;
  max-width: 1000px;
  grid-template-columns: repeat(10, 1fr);
  list-style: none;
  gap: 10px;
  background-color: #E6E6FA;
  padding: 8px;
  box-sizing: border-box;
}

.staff {
  cursor: pointer;
  padding: 4px 3px;
  text-align: center;
  font-size: 14px;
  user-select: none;
}

.sub-dept-name {
  font-weight: bold;
}

.bg-1 { background-color: white; }
.bg-2 { background-color: #F0E68C; }
.bg-3 { background-color: #00BFFF; }

.function {
  margin: 20px 0;
}

.function button {
  margin-right: 13px;
  padding: 8px;
}

.day, .note {
  margin: 20px 0;
}

ul {
  margin: 0;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* Responsive adjustments */
@media (max-width: 900px) {
  .staff-list { grid-template-columns: repeat(6, 1fr); }
}

@media (max-width: 700px) {
  body { font-size: 21px; }
  .staff-list { grid-template-columns: repeat(4, 1fr); }
  .staff { font-size: 21px; }
  button { font-size: 21px; }
  input { font-size: 21px; }
  select { font-size: 21px; }
}

@media (max-width: 480px) {
  body { font-size: 21px; }
  .staff-list { grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .staff { font-size: 21px; padding: 10px 0; }
  button { font-size: 21px; }
  input { font-size: 21px; }
  select { font-size: 21px; }
}
</style>
