
    // Initial data for the default chart
    let currentChartType = 'tran';
    let xValues = dataVisual.x_tran;
    let yValues = dataVisual.y_tran;
    
    const barColors = ["Green","DeepPink", "SandyBrown","AntiqueWhite","Lavender","Salmon", "aquamarine", "Teal", "violet", "red"];

    // Create a new chart
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: xValues,
            datasets: [{
                backgroundColor: barColors,
                data: yValues
            }]
        },
        options: {
            legend: { display: false },
            title: {
                display: true,
                text: "Transaction Summary"
            }
        }
    });

    function changeChart(chartType) {
        if (chartType === 'transaction') {
            xValues = dataVisual.x_tran;
            yValues = dataVisual.y_tran;
        } else if (chartType === 'account') {
            xValues = dataVisual.x_acct;
            yValues = dataVisual.y_acct;
        } else if (chartType === 'merchant') {
            xValues = dataVisual.x_merchant;
            yValues = dataVisual.y_merchant;
        }

        myChart.data.labels = xValues;
        myChart.data.datasets[0].data = yValues;
        myChart.options.title.text = `${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Summary`;
        myChart.update();
    }