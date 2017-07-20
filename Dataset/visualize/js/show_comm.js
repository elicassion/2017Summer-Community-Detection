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
let getLink = new Promise(function(resolve, reject){
    $.ajax({
        type: "get",
        url: "link.json",
        success: function(data){
            if (data.Status == "1"){
                resolve(data.ResultJson);
            } else{
                reject(data.ErrMsg);
            }
        }
    });
})

let getComm = new Promise(function(resolve,reject){
    $.ajax({
        type: "get",
        url: "comm.json",
        success: function(data){
            if (data.Status == "1"){
                resolve(data.ResultJson);
            } else{
                reject(data.ErrMsg);
            }
        }
    });
})

Promise.all([getLink,getComm]).then(function([linkJ, commJ]){
	let graph = {links:[], nodes:[]};
	let 
    let myChart = echarts.init(document.getElementById('main'));
	let categories = [];
	for (let i = 0; i < 9; i++) {
	    categories[i] = {
	        name: 'Comm-' + i
	    };
	}
})


// let option = {
//         title: {
//             text: 'Network',
//             subtext: 'Default layout',
//             top: 'bottom',
//             left: 'right'
//         },
//         tooltip: {},
//         legend: [{
//             // selectedMode: 'single',
//             data: categories.map(function (a) {
//                 return a.name;
//             })
//         }],
//         animationDuration: 1500,
//         animationEasingUpdate: 'quinticInOut',
//         series : [
//             {
//                 name: 'Les Miserables',
//                 type: 'graph',
//                 layout: 'none',
//                 data: graph.nodes,
//                 links: graph.links,
//                 categories: categories,
//                 roam: true,
//                 label: {
//                     normal: {
//                         position: 'right',
//                         formatter: '{b}'
//                     }
//                 },
//                 lineStyle: {
//                     normal: {
//                         color: 'source',
//                         curveness: 0.3
//                     }
//                 }
//             }
//         ]
//     };
// myChart.setOption(option);