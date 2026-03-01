function renderMacrosChart(protein, fat, carbs) {
  const ctx = document.getElementById("macrosChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Белки", "Жиры", "Углеводы"],
      datasets: [{
        data: [protein, fat, carbs]
      }]
    }
  });
}
