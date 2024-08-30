<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
const router = useRouter();
const route = useRoute();

const loading = ref(false);
const scores = ref(null);
const error = ref(null);

// watch the params of the route to fetch the data again
watch(() => route.params.id, fetchData, { immediate: true });

async function fetchItems(query) {
  const response = await fetch(`/api/scores/?${query}`);
  const scores = await response.json().then(items => items);
  return scores;
}

async function fetchData() {
  error.value = scores.value = null;
  loading.value = true;
  await router.isReady();
  // just passing query params directly to the api
  const query = new URLSearchParams(route.query).toString();
  try {
    scores.value = await fetchItems(query);
  } catch (err) {
    error.value = err.toString();
  } finally {
    loading.value = false;
  }
}
</script>
<template>
    <div id="scoreList">
    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="scores" class="content">
        <table class="table">
        <th>Revision ID</th>
        <th>Model Name</th>
        <th>Response Time</th>
        <tr v-for="(score, index) in scores" :key="index">
            <td>{{score.rev_id}}</td>
            <td>{{score.model_name}}</td>
            <td>{{score.true_probability}}</td>
            <td>{{score.status_code}}</td>
            <td>{{score.elapsed}}</td>
        </tr>
        </table>
    </div>
</div>
</template>
