document.addEventListener("DOMContentLoaded", function () {
    // Получаем данные, переданные через тег <script> в HTML
    const stats = JSON.parse(document.getElementById("chart-data").textContent);

    // Преобразование данных
    const labels = stats.map(stat => new Date(stat.date).toLocaleDateString()); // Преобразуем даты
    const data = stats.map(stat => parseFloat(stat.service_node_modem_change || 0)); // Преобразуем значения в числа

    // Логируем для отладки
    console.log("Метки (labels):", labels);
    console.log("Данные (data):", data);

    // Инициализация графика
    const ctx = document.getElementById('modemChangeChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels, // Даты
            datasets: [{
                label: 'Изменение стоимости приборов учета (в %)',
                data: data, // Данные
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
            },
            scales: {
                x: { title: { display: true, text: 'Дата' } },
                y: { title: { display: true, text: 'Изменение (%)' } }
            }
        }
    });
});
