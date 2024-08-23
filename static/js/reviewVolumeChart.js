document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/monthly-review-data/')
        .then(response => response.json())
        .then(data => {
            // 데이터가 정상적으로 로드되었는지 확인
            console.log('Data:', data);

            // 데이터 전처리
            const months = Array.from(new Set(data.map(d => d.month)));
            const brands = Array.from(new Set(data.map(d => d.brand_group)));

            // 각 브랜드의 데이터 준비
            const dataset = brands.map(brand => {
                return {
                    brand,
                    reviews: months.map(month => {
                        const entry = data.find(d => d.month === month && d.brand_group === brand);
                        return entry ? entry.review_count : 0;
                    })
                };
            });

            // 차트 설정
            const margin = { top: 20, right: 30, bottom: 40, left: 40 };
            const width = 800 - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;

            const svg = d3.select("#reviewVolumeChart")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);

            const x = d3.scaleBand()
                .domain(months)
                .range([0, width])
                .padding(0.1);

            const y = d3.scaleLinear()
                .domain([0, d3.max(dataset.flatMap(d => d.reviews))])
                .nice()
                .range([height, 0]);

            svg.append("g")
                .attr("class", "x-axis")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(x))
                .selectAll("text")
                .style("text-anchor", "middle");

            svg.append("g")
                .attr("class", "y-axis")
                .call(d3.axisLeft(y));

            // 바 차트 그리기
            brands.forEach((brand, index) => {
                svg.selectAll(`.bar-${brand}`)
                    .data(dataset.find(d => d.brand === brand).reviews)
                    .enter().append("rect")
                    .attr("class", `bar-${brand}`)
                    .attr("x", (d, i) => x(months[i]))
                    .attr("y", d => y(d))
                    .attr("width", x.bandwidth() / brands.length)
                    .attr("height", d => height - y(d))
                    .attr("fill", d3.schemeCategory10[index % 10]);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
});
