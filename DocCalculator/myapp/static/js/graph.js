document.addEventListener("DOMContentLoaded", function () {
    // �������� ������, ���������� ����� ��� <script> � HTML
    const stats = JSON.parse(document.getElementById("chart-data").textContent);

    // �������������� ������
    const labels = stats.map(stat => new Date(stat.date).toLocaleDateString()); // ����������� ����
    const data = stats.map(stat => parseFloat(stat.service_node_modem_change || 0)); // ����������� �������� � �����

    // �������� ��� �������
    console.log("����� (labels):", labels);
    console.log("������ (data):", data);

    // ������������� �������
    const ctx = document.getElementById('modemChangeChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels, // ����
            datasets: [{
                label: '��������� ��������� �������� ����� (� %)',
                data: data, // ������
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
                x: { title: { display: true, text: '����' } },
                y: { title: { display: true, text: '��������� (%)' } }
            }
        }
    });
});
