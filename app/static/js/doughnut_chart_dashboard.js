function createDoughnutChart(customData) {
    const dataDoughnut = {
      labels: customData.map(dataPoint => dataPoint.label),
      datasets: [
        {
          label: "Number of channels",
          data: customData.map(dataPoint => dataPoint.value),
          backgroundColor: [
            "rgb(92, 75, 81)",
            "rgb(140, 190, 178)",
            "rgb(242, 235, 191)",
            "rgb(243, 181, 98)",
            "rgb(240, 96, 96)",
          ],
          hoverOffset: 4,
        },
      ],
    };
    
    const configDoughnut = {
      type: "doughnut",
      data: dataDoughnut,
      options: {},
    };
    
    var chartBar = new Chart(
      document.getElementById("chartDoughnut"),
      configDoughnut
    );
  }
  
          // const dataDoughnut = {
        //   labels: ["JavaScript", "Python", "Ruby"],
        //   datasets: [
        //     {
        //       label: "My First Dataset",
        //       data: [300, 50, 100],
        //       backgroundColor: [
        //         "rgb(133, 105, 241)",
        //         "rgb(164, 101, 241)",
        //         "rgb(101, 143, 241)",
        //       ],
        //       hoverOffset: 4,
        //     },
        //   ],
        // };
