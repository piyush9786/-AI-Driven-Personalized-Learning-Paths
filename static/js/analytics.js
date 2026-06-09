// ========== Performance Line Chart (Courses Completed or Avg Progress) ==========
const performanceCtx = document.getElementById('performanceChart').getContext('2d');
new Chart(performanceCtx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Avg Progress (%)',
      data: [60, 63, 65, 68, 70, 72],
      borderColor: '#00ffcc',
      backgroundColor: 'transparent',
      pointBackgroundColor: '#00ffcc',
      borderWidth: 2,
      tension: 0.4
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { labels: { color: '#ccc' } } },
    scales: {
      x: { ticks: { color: '#ccc' }, grid: { display: false } },
      y: { ticks: { color: '#ccc' }, grid: { color: '#333' } }
    }
  }
});

// ========== Growth Chart ==========
const growthCtx = document.getElementById('growthChart').getContext('2d');
new Chart(growthCtx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Active Learners',
      data: [800, 900, 950, 1000, 1100, 1200],
      borderColor: '#6c5ce7',
      borderWidth: 2,
      fill: false,
      tension: 0.4,
      pointBackgroundColor: '#6c5ce7'
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { labels: { color: '#ccc' } } },
    scales: {
      x: { ticks: { color: '#ccc' }, grid: { display: false } },
      y: { ticks: { color: '#ccc' }, grid: { color: '#333' } }
    }
  }
});

// ========== Course Category Engagement ==========
const categoryCtx = document.getElementById('categoryEngagement').getContext('2d');
new Chart(categoryCtx, {
  type: 'doughnut',
  data: {
    labels: ['AI/ML', 'Web Dev', 'Data Science', 'Cybersecurity', 'Cloud'],
    datasets: [{
      data: [30, 25, 20, 15, 10],
      backgroundColor: ['#ff4c93', '#00c9a7', '#8e44ad', '#f39c12', '#3498db']
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        labels: { color: '#ccc' }
      }
    }
  }
});

// ========== Login Patterns ==========
const loginCtx = document.getElementById('loginPatterns').getContext('2d');
new Chart(loginCtx, {
  type: 'bar',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Morning',
        data: [40, 30, 35, 32, 50, 65, 30],
        backgroundColor: '#00c9a7'
      },
      {
        label: 'Evening',
        data: [60, 50, 55, 48, 65, 70, 35],
        backgroundColor: '#ff4c93'
      }
    ]
  },
  options: {
    responsive: true,
    scales: {
      x: { ticks: { color: '#ccc' }, grid: { display: false } },
      y: { ticks: { color: '#ccc' }, grid: { color: '#333' } }
    }
  }
});

// ========== Age Demographics ==========
const ageCtx = document.getElementById('ageDemographics').getContext('2d');
new Chart(ageCtx, {
  type: 'bar',
  data: {
    labels: ['18-24', '25-34', '35-44', '45-54', '55+'],
    datasets: [
      {
        label: 'Male',
        data: [300, 400, 350, 200, 150],
        backgroundColor: '#00c9a7'
      },
      {
        label: 'Female',
        data: [280, 420, 370, 180, 100],
        backgroundColor: '#ff4c93'
      }
    ]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    scales: {
      x: { ticks: { color: '#ccc' }, grid: { color: '#333' } },
      y: { ticks: { color: '#ccc' }, grid: { display: false } }
    }
  }
});
