<template>
  <div id="app">
    <Navigator />

    <Highcharts />
  </div>
</template>

<script>
import Navigator from "./components/Navigator.vue";
import Highcharts from "./components/Highcharts.vue";

export default {
  name: "app",
  components: {
    Navigator,
    Highcharts
  }
};
</script>

<style>
/* #app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0;
} */
</style>
