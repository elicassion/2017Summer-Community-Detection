// graph{
// 	links:[
// 		{
// 			id:"",
// 			lineStyle:{
// 				normal:{}
// 			},
// 			name:,
// 			source:"1",
// 			target:"0"
// 		}
// 	]
// 	nodes:[
// 		{
// 			attributes:{
// 				modularity_class:0
// 			},
// 			category:0,
// 			id:"0",
// 			itemStyle:,
// 			label:{
// 				normal:{
// 					show:false
// 				}
// 			},
// 			name:"",
// 			symbolSize: 20,
// 			value: 20,
// 		}
// 	]
// }
let prefix = "birthdeath";
let t_step = "t05";
// console.log("data/"+prefix+'.'+t_step+'.json');



let dataUrl = "data/"+prefix+'.'+t_step+'.json';
$.getJSON(dataUrl, function(gJson){
    let graph = gJson;
    console.log(graph);
    let myChart = echarts.init(document.getElementById('main'));
    let categories = [];
    for (let i = 0; i < 32; i++) {
        categories[i] = {
            name: 'Comm-' + i
        };
    }
    let option = {
        title: {
            text: 'Network',
            subtext: 'Default layout',
            top: 'bottom',
            left: 'right'
        },
        tooltip: {},
        legend: [{
            // selectedMode: 'single',
            data: categories.map(function (a) {
                return a.name;
            })
        }],
        animationDuration: 1500,
        animationEasingUpdate: 'quinticInOut',
        series : [
            {
                name: 'Les Miserables',
                type: 'graph',
                layout: 'none',
                data: graph.nodes,
                links: graph.links,
                categories: categories,
                roam: true,
                label: {
                    normal: {
                        position: 'right',
                        formatter: '{b}'
                    }
                },
                lineStyle: {
                    normal: {
                        color: 'source',
                        curveness: 0.3
                    }
                }
            }
        ]
    };
    myChart.setOption(option);
})
