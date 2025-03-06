document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const productInput = document.getElementById('productInput');
    const loadingScreen = document.querySelector('.loading-screen');
    const results = document.querySelector('.results');
    
    let sustainabilityChart, costChart, impactChart;

    function initializeCharts() {
        // Sustainability Chart
        sustainabilityChart = new Chart(document.getElementById('sustainabilityChart'), {
            type: 'radar',
            data: {
                labels: Object.keys(packagingMaterials),
                datasets: [{
                    label: 'Sustainability Score',
                    data: [0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    pointBackgroundColor: 'rgba(46, 204, 113, 1)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // Cost Chart
        costChart = new Chart(document.getElementById('costChart'), {
            type: 'bar',
            data: {
                labels: ['Material', 'Production', 'Transportation', 'Recycling'],
                datasets: [{
                    label: 'Cost Efficiency',
                    data: [0, 0, 0, 0],
                    backgroundColor: 'rgba(46, 204, 113, 0.6)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // Environmental Impact Chart
        impactChart = new Chart(document.getElementById('impactChart'), {
            type: 'doughnut',
            data: {
                labels: ['Carbon Footprint', 'Water Usage', 'Energy Consumption', 'Waste Generation'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(46, 204, 113, 0.6)',
                        'rgba(52, 152, 219, 0.6)',
                        'rgba(155, 89, 182, 0.6)',
                        'rgba(241, 196, 15, 0.6)'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    function updateCharts(productData) {
        // Update Sustainability Chart
        sustainabilityChart.data.datasets[0].data = Object.values(productData.sustainability);
        sustainabilityChart.update();

        // Update Cost Chart
        costChart.data.datasets[0].data = Object.values(productData.costs);
        costChart.update();

        // Update Impact Chart
        impactChart.data.datasets[0].data = Object.values(productData.impact);
        impactChart.update();

        // Update Material Properties
        const propertiesDiv = document.getElementById('materialProperties');
        propertiesDiv.innerHTML = '<h3>Material Properties</h3>';
        Object.entries(productData.properties).forEach(([property, value]) => {
            propertiesDiv.innerHTML += `
                <div class="property-item">
                    <span>${property}</span>
                    <span>${value}</span>
                </div>
            `;
        });

        // Update recommended material and eco score
        document.getElementById('recommendedMaterial').textContent = productData.recommended;
        document.querySelector('.score-value').textContent = productData.ecoScore;
    }

    // Add autocomplete functionality
    const productList = Object.keys(productDatabase).map(key => productDatabase[key].name);
    const dataList = document.createElement('datalist');
    dataList.id = 'products';
    productList.forEach(product => {
        const option = document.createElement('option');
        option.value = product;
        dataList.appendChild(option);
    });
    document.body.appendChild(dataList);
    productInput.setAttribute('list', 'products');

    analyzeBtn.addEventListener('click', function() {
        const product = productInput.value.toLowerCase();
        
        if (!product) {
            alert('Please enter a product name');
            return;
        }

        loadingScreen.classList.remove('hidden');
        results.classList.add('hidden');

        setTimeout(() => {
            loadingScreen.classList.add('hidden');
            
            const productData = productDatabase[product];
            if (productData) {
                results.classList.remove('hidden');
                
                if (!sustainabilityChart) {
                    initializeCharts();
                }
                
                updateCharts(productData);
            } else {
                alert('Product not found in database. Please try another product.');
            }
        }, 2000);
    });

    // Initialize charts on page load
    initializeCharts();
});