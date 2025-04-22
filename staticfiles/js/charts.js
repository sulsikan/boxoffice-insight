// 차트 객체를 저장할 변수
let revenueChart = null;
let donutChart = null;

// 차트 색상
const chartColors = {
    'US': 'rgba(54, 162, 235, 0.8)',
    'UK': 'rgba(255, 99, 132, 0.8)',
    'DE': 'rgba(255, 206, 86, 0.8)',
    'JP': 'rgba(75, 192, 192, 0.8)'
};

// 국가 이름 매핑
const countryNames = {
    'US': '미국',
    'UK': '영국',
    'DE': '독일',
    'JP': '일본'
};

// 차트 초기화 함수
function initializeCharts() {
    const barCtx = document.getElementById('revenueChart').getContext('2d');
    const donutCtx = document.getElementById('donutChart').getContext('2d');

    // 막대 그래프 설정
    revenueChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: Object.values(countryNames),
            datasets: [{
                label: '매출액 (백만)',
                data: [0, 0, 0, 0],
                backgroundColor: Object.values(chartColors)
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '매출액 (백만)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: '국가별 매출 순위'
                }
            }
        }
    });

    // 도넛 차트 설정
    donutChart = new Chart(donutCtx, {
        type: 'doughnut',
        data: {
            labels: Object.values(countryNames),
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: Object.values(chartColors)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '국가별 매출 비중'
                }
            }
        }
    });
}

// 데이터 업데이트 함수
async function updateCharts() {
    const year = document.getElementById('yearSelect').value;
    const period = document.getElementById('periodSelect').value;

    try {
        const response = await fetch(`/api/revenue?year=${year}&period=${period}`);
        const data = await response.json();

        // 데이터 업데이트
        revenueChart.data.datasets[0].data = Object.values(data);
        donutChart.data.datasets[0].data = Object.values(data);

        // 차트 업데이트
        revenueChart.update();
        donutChart.update();
    } catch (error) {
        console.error('데이터 로딩 중 오류 발생:', error);
    }
}

// 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    
    // 조회 버튼 클릭 이벤트
    document.getElementById('updateChart').addEventListener('click', updateCharts);
}); 