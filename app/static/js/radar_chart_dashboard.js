function createChart(labels, data, username) {
    const chartData = {
        labels: labels,
        datasets: [{
            label: username,
            data: data,
            fill: true,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgb(255, 99, 132)',
            pointBackgroundColor: 'rgb(255, 99, 132)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(255, 99, 132)'
        }]
    };

    const chartConfig = {
        type: 'radar',
        data: chartData,
        options: {
            scale: {
                min: 0,
            },
            elements: {
                line: {
                    borderWidth: 3
                }
            }
        },
    };

    const ctx = document.getElementById('radar_chart').getContext('2d');
    const myChart = new Chart(ctx, chartConfig);
}
